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
from odoo import fields, models, api, _
from datetime import datetime, timedelta
from openerp.exceptions import Warning
import time
from pytz import timezone
from odoo.tools import float_is_zero


class pos_reorder(models.Model):
    _inherit = "pos.order"

    amount_due = fields.Float(string='Amount Due', compute='_compute_amount_due')
    is_delivery = fields.Boolean(string='Deliver')
    customer_email = fields.Char('Customer Email')

    @api.model
    def create_from_ui(self, orders):
        for each_data in orders:
            credit_details = each_data['data'].get('credit_detail')
            if credit_details:
                self.env['account.invoice'].get_credit_info(credit_details)
        res = super(pos_reorder, self).create_from_ui(orders)
        return res

    @api.multi
    def _compute_amount_due(self):
        for each in self:
            each.amount_due = each.amount_total - each.amount_paid

    @api.multi
    def action_pos_order_paid(self):
        if self.is_delivery and not self.test_paid() and not self.picking_id:
            self.create_picking()
            return
        elif self.test_paid() and self.picking_id:
            self.write({'state': 'paid'})
            return True
        else:
            return super(pos_reorder, self).action_pos_order_paid()

    @api.model
    def _process_order(self, order):
        pos_line_obj = self.env['pos.order.line']
        draft_order_id = order.get('old_order_id')
        if order.get('draft_order'):
            if not draft_order_id:
                order.pop('draft_order')
                order_id = self.create(self._order_fields(order))
                return order_id
            else:
                order_id = draft_order_id
                pos_line_ids = pos_line_obj.search([('order_id', '=', order_id)])
                if pos_line_ids:
                    pos_line_obj.unlink(pos_line_ids)
                self.write([order_id],
                           {'lines': order['lines'],
                            'partner_id': order.get('partner_id')})
                return order_id

        if not order.get('draft_order') and draft_order_id:
            order_id = draft_order_id
            order_obj = self.browse(order_id)
            temp = {}
            pos_line_ids = pos_line_obj.search([('order_id', '=', order_id)])
            if pos_line_ids:
                for line_id in pos_line_ids:
                    line_id.unlink()
            temp = order.copy()
            temp.pop('statement_ids', None)
            temp.pop('name', None)
            temp.update({
                'date_order': order.get('creation_date')
            })
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

        if not order.get('draft_order') and not draft_order_id:
            order_id = super(pos_reorder, self)._process_order(order)
            return order_id

    @api.model
    def ac_pos_search_read(self, domain):
        domain = domain.get('domain')
        search_vals = self.search_read(domain)
        user_id = self.env['res.users'].browse(self._uid)
        tz = False
        if self._context and self._context.get('tz'):
            tz = timezone(self._context.get('tz'))
        elif user_id and user_id.tz:
            tz = timezone(user_id.tz)
        if tz:
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            today_sale = 0.0
            result = []
            for val in search_vals:
                if sign == '-':
                    val.update({
                        'date_order':(datetime.strptime(val.get('date_order'), '%Y-%m-%d %H:%M:%S') - timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                elif sign == '+':
                    val.update({
                        'date_order':(datetime.strptime(val.get('date_order'), '%Y-%m-%d %H:%M:%S') + timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                result.append(val)
            return result
        else:
            return search_vals

class pos_config(models.Model):
    _inherit = "pos.config"

    last_days = fields.Integer("Last Days")
    record_per_page = fields.Integer("Record Per Page")
    prod_for_payment = fields.Many2one('product.product',string='Paid Amount Product',
                                      help="This is a dummy product used when a customer pays partially. This is a workaround to the fact that Odoo needs to have at least one product on the order to validate the transaction.")


class account_journal(models.Model):
    _inherit="account.journal"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('config_jr'):
            if self._context.get('journal_ids') and \
                    self._context.get('journal_ids')[0] and \
                    self._context.get('journal_ids')[0][2]:
                args += [['id', 'in', self._context.get('journal_ids')[0][2]]]
            else:
                return False;
        return super(account_journal, self).name_search(name, args=args, operator=operator, limit=limit)


class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def create(self, values):
        if values.get('product_id') and not values.get('from_credit'):
            if self.env['pos.order'].browse(values['order_id']).session_id.config_id.prod_for_payment.id == values.get('product_id'):
                return
        return super(pos_order_line, self).create(values)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _confirm_orders(self):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id, default=session.config_id.journal_id.id)

            move = self.env['pos.order'].with_context(force_company=company_id)._create_account_move(session.start_at, session.name, int(journal_id), company_id)
            orders.with_context(force_company=company_id)._create_account_move_line(session, move)
            for order in session.order_ids.filtered(lambda o: o.state not in ['done', 'invoiced']):
                if order.state not in ('draft'):
                    order.action_pos_order_done()

    @api.multi
    def action_pos_session_open(self):
        pos_order = self.env['pos.order'].search([('state', '=', 'draft')])
        for order in pos_order:
            if order.session_id.state != 'opened':
                order.write({'session_id': self.id})
        return super(PosSession, self).action_pos_session_open()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: