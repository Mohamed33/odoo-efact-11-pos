# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"
    def _order_fields(self,ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'note': ui_order.get('order_note') or False
        })
        return res

    @api.model
    def create_from_ui(self, orders):
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        order_to_update = [o for o in orders if o['data']['name'] in existing_references]
        # Keep only new orders
        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)
            order_ids.append(pos_order.id)

            try:
                pos_order.action_pos_order_paid()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                pos_order.action_pos_order_invoice()
                pos_order.invoice_id.sudo().action_invoice_open()
                pos_order.account_move = pos_order.invoice_id.move_id

        # Update draft orders
        for tmp_order in order_to_update:
            for order in pos_order:
                if order.pos_reference == tmp_order['data']['name']:
                    pos_line_ids = self.env['pos.order.line'].search([('order_id', '=', order.id)])
                    if pos_line_ids:
                        pos_cids = []
                        for line_id in pos_line_ids:
                            pos_cids.append(line_id.pos_cid)
                            for line in tmp_order['data']['lines']:
                                if line_id.pos_cid == line[2].get('pos_cid'):
                                    order.write({'lines': [(1, line_id.id, line[2])]})

                        for line in tmp_order['data']['lines']:
                            if line[2].get('pos_cid') not in pos_cids:
                                order.write({'lines': [(0, 0, line[2])]})

                    to_invoice = tmp_order['to_invoice']
                    order = tmp_order['data']
                    if to_invoice:
                        self._match_payment_to_invoice(order)
                    pos_order = self._process_order(order)
                    order_ids.append(pos_order.id)

                    try:
                        pos_order.action_pos_order_paid()
                    except psycopg2.OperationalError:
                        # do not hide transactional errors, the order(s) won't be saved!
                        raise
                    except Exception as e:
                        _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

                    if to_invoice:
                        pos_order.action_pos_order_invoice()
                        pos_order.invoice_id.sudo().action_invoice_open()
                        pos_order.account_move = pos_order.invoice_id.move_id
        self.broadcast_order_data(True)
        # customer_screen = self.env['pos.config'].compute_customer_screen_orders_html()
        # print("\n\n\n\n\n\n\ncreate_from_ui=====================\n\n\n\n",customer_screen);

        return order_ids

    @api.model
    def _process_order(self, order):
        submitted_references = order['name']
        draft_order_id = self.search([('pos_reference', '=', submitted_references)]).id

        if draft_order_id:
            order_id = draft_order_id
            order_obj = self.browse(order_id)
            temp = order.copy()
            temp.pop('statement_ids', None)
            temp.pop('name', None)
            temp.pop('lines',None)
            order_obj.write(temp)
            for payments in order['statement_ids']:
                order_obj.add_payment(self._payment_fields(payments[2]))

            session = self.env['pos.session'].browse(order['pos_session_id'])
            if session.sequence_number <= order['sequence_number']:
                session.write({'sequence_number': order['sequence_number'] + 1})
                session.refresh()

            if not float_is_zero(order['amount_return'], self.env['decimal.precision'].precision_get('Account')):
                cash_journal = session.cash_journal_id
                if not cash_journal:
                    cash_journal_ids = session.statement_ids.filtered(lambda st: st.journal_id.type == 'cash')
                    if not len(cash_journal_ids):
                        raise Warning(_('error!'),
                                      _("No cash statement found for this session. Unable to record returned cash."))
                    cash_journal = cash_journal_ids[0].journal_id
                order_obj.add_payment({
                    'amount': -order['amount_return'],
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('return'),
                    'journal': cash_journal.id,
                })
            return order_obj

        if not draft_order_id:
            order_id = super(PosOrder, self)._process_order(order)
            return order_id

    @api.model
    def broadcast_order_data(self, new_order):
        notifications = []
        pos_order = self.search([('lines.state', 'not in', ['cancel', 'done'])])
        screen_table_data = []
        for order in pos_order:
            order_line_list = []
            for line in order.lines:
                order_line = {
                    'id': line.id,
                    'name': line.product_id.product_tmpl_id.name,
                    'qty': line.qty,
                    'table': line.order_id.table_id.name,
                    'floor': line.order_id.table_id.floor_id.name,
                    'time': self.get_time(line.create_date),
                    'state': line.state,
                    'note': line.order_line_note,
                    'categ_id': line.product_id.product_tmpl_id.pos_categ_id.id,
                    'order': line.order_id.id,
                    'pos_cid': line.pos_cid,
                    'user': line.create_uid.id,
                    'route_id': line.product_id.product_tmpl_id.route_ids.active,
                }
                order_line_list.append(order_line)
            order_dict = {
                'order_id': order.id,
                'order_name': order.name,
                'order_time': self.get_time(order.create_date),
                'table': order.table_id.name,
                'floor': order.table_id.floor_id.name,
                'customer': order.partner_id.name,
                'order_lines': order_line_list,
                'total': order.amount_total,
                'note': order.note,
            }
            screen_table_data.append(order_dict)
        vals = {
            "orders": screen_table_data,
        }
        if new_order:
            vals['new_order'] = new_order
        pos_session = self.env['pos.session'].search([('state', '=', 'opened')])
        for session in pos_session:
            notifications.append(
                ((self._cr.dbname, 'pos.order.line', session.user_id.id), ('screen_display_data', vals)))
            self.env['bus.bus'].sendmany(notifications)
        return True

    @api.multi
    def get_time(self, date_time):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '-':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '+':
            date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=hour_tz, minutes=min_tz)
        return str(date.strftime("%Y-%m-%d %H:%M:%S"))

#     @api.multi
#     def get_session_date(self, line):
#         SQL = """SELECT create_date AT TIME ZONE 'GMT' as create_date  from pos_order_line where id = %d
#                    """ % (line.id)
#         self._cr.execute(SQL)
#         data = self._cr.dictfetchall()
#         time = data[0]['create_date']
#         return str(time.hour)+ ':' + str(time.minute) + ':' + str(time.second)
# 
#     @api.multi
#     def get_order_date(self, order):
#         SQL = """SELECT date_order AT TIME ZONE 'GMT' as date_order  from pos_order where id = %d
#                        """ % (order.id)
#         self._cr.execute(SQL)
#         data = self._cr.dictfetchall()
#         time = data[0]['date_order']
#         return str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)

class PosOrderLines(models.Model):
    _inherit = "pos.order.line"

    @api.model
    def update_orderline_state(self,vals):
        order_line = self.browse(vals['order_line_id'])
        res = order_line.sudo().write({
            'state': vals['state']
        });
        vals['pos_reference'] = order_line.order_id.pos_reference
        vals['pos_cid'] = order_line.pos_cid
        self.env['bus.bus'].sendone((self._cr.dbname, 'pos.order.line',  order_line.create_uid.id), ('order_line_state', vals))
        return res

    state = fields.Selection(selection=[("waiting", "Waiting"), ("preparing", "Preparing"), ("delivering", "Waiting/deliver"),("done","Done"),("cancel","Cancel")],default="waiting")
    order_line_note = fields.Text("Order Line Notes")
    pos_cid = fields.Char("pos cid")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: