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

from odoo import netsvc, tools, models, fields, api, _
import time
from datetime import datetime, timedelta
import psycopg2
from pytz import timezone
from odoo.tools import float_is_zero
import os
import json
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.profiler import profile

class pos_order(models.Model):
    _inherit = "pos.order"

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)

            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_digits=l.product_id.uom_id.rounding) and not l.operation_product):
                moves |= Move.create({
                    'name': line.name,
                    'restrict_lot_id':line.prodlot_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })
            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
                return_picking.action_done()

            if order_picking:
                order._force_picking_done(order_picking)
                order_picking.action_done()

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                tracked_moves = moves.filtered(lambda move: move.product_id.tracking != 'none')
                untracked_moves = moves - tracked_moves
                tracked_moves.action_confirm()
                untracked_moves.action_assign()
                moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none').action_done()

        return True

    @api.multi
    # @api.depends('lines')
    def _return_status(self):
        for order in self:
            if not order.back_order:
                full = [ line for line in order.lines if line.return_qty > 0 and not line.product_id.non_refundable ]
                if not full:
                    order.return_status = 'full'
                    continue
                partial = [ line for line in order.lines if line.return_qty < line.qty and not line.product_id.non_refundable ]
                if partial:
                    order.return_status = 'partial'
                    continue
                if full and not partial:
                    order.return_status = 'nothing'
                    continue

    return_status = fields.Selection([('nothing', ''), ('partial', 'Partially Returned'), ('full', 'Fully Returned')], "Return Status", compute="_return_status",default="nothing")
    return_process = fields.Boolean('Return Process')
    back_order = fields.Char('Back Order', size=256, default=False, copy=False)

    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        res.update({
            'back_order': ui_order.get('back_order', '') or False,
        })
        return res
    
    @api.model
    def _process_order(self, order):
        """"
        [{
            id: 6187591311, 
            to_invoice: false, 
            data: {partner_id: false, 
                    back_order: , 
                    uid: 6187591311, 
                    amount_return: 28, 
                    number: false, 
                    fiscal_position_id: false, 
                    lines: [[0, 0, {exchange_product: false, 
                                    return_qty: 1, 
                                    id: 33, 
                                    pack_lot_ids: [[0, 0, {lot_name: 123456qw}]], 
                                    stock_income: false, 
                                    tax_ids: [[6, false, [1]]], 
                                    discount: 0, qty: 1, 
                                    operation_product: false, 
                                    prodlot_id: 9, 
                                    product_id: 11,
                                    price_unit: 62}]], 
                    pos_session_id: 1, 
                    invoice_journal: false, 
                    user_id: 1, 
                    amount_total: 62, 
                    sale_order_name: false, 
                    sequence_number: 0, 
                    statement_ids: [[0, 0, {statement_id: 1, 
                                            account_id: 1541, 
                                            amount: 90, 
                                            name: 2018-12-30 16:33:22, 
                                            journal_id: 6}]], 
                    amount_tax: 9.457627, 
                    amount_paid: 90, 
                    creation_date: 2018-12-30T16:33:22.132Z, 
                    pricelist_id: 1, 
                    name: Pedido6187591311
                }
            }
        ]
        """
        order_id = self.with_context(from_pos=True).create(self._order_fields(order))
        os.system('echo "%s"'%("_process_order"))
        os.system('echo "%s"'%(order_id.id))
        for payments in order['statement_ids']:
            if not order.get('sale_mode') and order.get('parent_return_order', ''):
                payments[2]['amount'] = payments[2]['amount'] or 0.0
            order_id.add_payment(self._payment_fields(payments[2]))

        os.system('echo "%s"'%("add_payment"))
        os.system('echo "%s"'%(order_id.id))

        session = self.env['pos.session'].browse(order['pos_session_id'])
        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        os.system('echo "%s"'%("set_session"))
        os.system('echo "%s"'%(order_id.id))

        if not order.get('parent_return_order', '') and not float_is_zero(order['amount_return'], self.env['decimal.precision'].precision_get('Account')):
            cash_journal = session.cash_journal_id
            if not cash_journal:
                cash_journal_ids = list(filter(lambda st: st.journal_id.type == 'cash', session.statement_ids))
                if not len(cash_journal_ids):
                    raise Warning(_('error!'),
                        _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0].journal_id
            order_id.add_payment({
                'amount':-order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal.id,
            })
        
        if order.get('parent_return_order', '') and not float_is_zero(order['amount_return'], self.env['decimal.precision'].precision_get('Account')):
            cash_journal = session.cash_journal_id
            if not cash_journal:
                cash_journal_ids = list(filter(lambda st: st.journal_id.type == 'cash', session.statement_ids))
                if not len(cash_journal_ids):
                    raise Warning(_('error!'),
                        _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0].journal_id
            order_id.add_payment({
                'amount':-order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal.id,
            })
        return order_id

    @api.model
    def create_from_ui(self, orders):
        # Keep only new orders
        os.system('echo "%s"'%(json.dumps(orders)))
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)

            os.system('echo "%s"'%(pos_order.id))
            if pos_order :
                to_be_returned_items = {}
                for line in order.get('lines'):
                    if line[2].get('return_process'):
                        if line[2].get('product_id') in to_be_returned_items:
                            to_be_returned_items[line[2].get('product_id')] = to_be_returned_items[line[2].get('product_id')] + line[2].get('qty')
                        else:
                            to_be_returned_items.update({line[2].get('product_id'):line[2].get('qty')})
                for line in order.get('lines'):
                    for item_id in to_be_returned_items:
                        return_lines = []
                        if line[2].get('return_process'):
                            return_lines = self.browse([line[2].get('return_process')[0]]).lines
                        for origin_line in return_lines:
                            if to_be_returned_items[item_id] == 0:
                                continue
                            if origin_line.return_qty > 0 and item_id == origin_line.product_id.id:
                                if (to_be_returned_items[item_id] * -1) >= origin_line.return_qty:
                                    ret_from_line_qty = 0
                                    to_be_returned_items[item_id] = to_be_returned_items[item_id] + origin_line.return_qty
                                else:
                                    ret_from_line_qty = to_be_returned_items[item_id] + origin_line.return_qty
                                    to_be_returned_items[item_id] = 0

                                origin_line.write({'return_qty': ret_from_line_qty})
            order_ids.append(pos_order.id)
            os.system('echo "%s"'%(str(order_ids)))
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
            os.system('echo "%s"'%("despues de pagar"))
            if to_invoice:
                pos_order.action_pos_order_invoice()
                pos_order.invoice_id.sudo().action_invoice_open()
                pos_order.account_move = pos_order.invoice_id.move_id

        return order_ids

    @api.model
    def add_payment(self, data):
        """Create a new payment for the order"""
        if data['amount'] == 0.0:
            return
        return super(pos_order, self).add_payment(data)

    @api.model
    def ac_pos_search_read(self, domain):
        search_vals = self.search_read(domain)
        user_id = self.env['res.users'].browse(self._uid)
        tz = False
        result = []
        if self._context and self._context.get('tz'):
            tz = timezone(self._context.get('tz'))
        elif user_id and user_id.tz:
            tz = timezone(user_id.tz)
        if tz:
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
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

    @profile
    def _action_create_invoice_line(self, line=False, invoice_id=False):
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty,
            'account_analytic_id': self._prepare_analytic_account(line),
            'name': inv_name,
            'prodlot_id': line.prodlot_id.id
        }
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id).ids
        fiscal_position_id = line.order_id.fiscal_position_id
        if fiscal_position_id:
            invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids, line.product_id, line.order_id.partner_id)
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.ids
        # We convert a new id object back to a dictionary to write to
        # bridge between old and new api
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update({"price_unit":line.price_unit, "discount":line.discount})
        return InvoiceLine.sudo().create(inv_line)

class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    return_qty = fields.Float("Return Quantity")
    return_process = fields.Char('Return Process')
    back_order = fields.Char('Back Order', size=256, default=False, copy=False)
    prodlot_id = fields.Many2one('stock.production.lot', "Serial No.")
    exchange_product = fields.Boolean("Exchange Product")
    operation_product = fields.Boolean("Operation Product")
    stock_income = fields.Boolean("Stock Income")

class PosConfig(models.Model):
    _inherit = "pos.config"

    so_operation_draft = fields.Boolean("SO Operation Quotation")
    so_operation_confirm = fields.Boolean("SO Operation Confirm")
    so_operation_paid = fields.Boolean("SO Operation Paid")
    enable_add_product = fields.Boolean("Enable Product Operations")
    enable_pos_serial = fields.Boolean("Enable POS serials")

    last_days = fields.Char("Last Days")
    load_current_session_order = fields.Boolean("Load Order Of Current Session Only")
    specified_orders = fields.Boolean("Load Orders From Past Upto Specified Number Of Days")
    so_sequence = fields.Many2one('ir.sequence',"Sale Order sequence")


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
 
    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self._context.get('from_pos'):
            super(AccountBankStatementLine, self)._check_amount()

    @api.one
    @api.constrains('amount', 'amount_currency')
    def _check_amount_currency(self):
        if not self._context.get('from_pos'):
            super(AccountBankStatementLine, self)._check_amount_currency()

class product_product(models.Model):
    _inherit="product.product"

    non_refundable = fields.Boolean("Non Refundable")


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    prodlot_id = fields.Many2one('stock.production.lot', "Serial No.")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: