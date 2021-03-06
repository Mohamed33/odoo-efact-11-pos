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
from odoo.tools import float_compare
import json
import os
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        if vals.get('codigo_battery') and vals.get('type') == 'product':
            vals.update({'tracking' : 'serial'})
        res = super(ProductTemplate, self).create(vals)
        return res
    
    def add_lot_serials(self, vals):
        os.system('echo "%s"'%(json.dumps(vals)))
        if vals.get('codigo_battery') and vals.get('type') == 'product' and vals.get('product_tmpl_id'):
            prod_rec = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            if prod_rec:
                prod_rec.write({'tracking' : 'serial'})
            prod_id = self.env['product.product'].search([('product_tmpl_id', '=', vals.get('product_tmpl_id'))])
            if prod_id and vals.get('location_id'):
                lot_id = self.env['stock.production.lot'].create({'product_id':prod_id.id, 'name':vals.get('codigo_battery')})
                update_qty_id = self.env['stock.change.product.qty'].create({'product_id' : prod_id.id,
                                                                             'location_id' : vals.get('location_id'),
                                                                             'new_quantity':1.0, 'lot_id' : lot_id.id})
                update_qty_id.change_product_qty()
                if lot_id:
                    return lot_id.id
                return False

class sale_order(models.Model):
    _inherit = "sale.order"

    session_id = fields.Many2one('pos.session', "POS Session", readonly=True)
    location_id = fields.Many2one('stock.location', 'Location', related="")

    @api.model
    def create_sales_order(self, orderline, customer_id, session_id, location_id, journals, sequence_id):
        sale_pool = self.env['sale.order']
        prod_pool = self.env['product.product']
        sale_line_pool = self.env['sale.order.line']
        seq_code = False
        if sequence_id:
            seq_code = self.env['ir.sequence'].browse(sequence_id[0]).code
        if customer_id:
            customer_id = int(customer_id)
            sale = {
                'partner_id': customer_id,
                'partner_invoice_id': customer_id,
                'partner_shipping_id': customer_id,
                'session_id': session_id,
                'location_id': location_id,
            }
            new = sale_pool.new({'partner_id': customer_id})
            new.onchange_partner_id()
            sale_id = sale_pool.with_context(from_pos=True, sequence_code = seq_code).create(sale)
            # create sale order line
            sale_line = {'order_id': sale_id.id}
            for line in orderline:
                # 'sale_prodlot_id': line.get('prodlot_id', False)
                prod_rec = prod_pool.browse(line['product_id'])
                sale_line.update({'name': prod_rec.name or False,
                                  'product_id': prod_rec.id,
                                  'product_uom_qty': line['qty'],
                                  'discount': line.get('discount'),
                                  'lot_id':line.get('prodlot_id', False),
                                  'from_pos' :True,
                                  })
                new_prod = sale_line_pool.new({'product_id': prod_rec.id})
                prod = new_prod.product_id_change()
                sale_line.update(prod)
                sale_line.update({'price_unit': line['price_unit']})
                taxes = map(lambda a: a.id, prod_rec.taxes_id)
                if sale_line.get('tax_id'):
                    sale_line.update({'tax_id': sale_line.get('tax_id')})
                elif taxes:
                    sale_line.update({'tax_id': [(6, 0, taxes)]})
                sale_line.pop('domain')
                sale_line.update({'product_uom': prod_rec.uom_id.id})
                sale_line_pool.with_context(from_pos=True).create(sale_line)
            if self._context.get('confirm'):
                sale_id.action_confirm()
            if self._context.get('paid'):
                sale_id.action_confirm()
                if not sale_id.delivery_order(location_id):
                    return False
                inv_id = sale_id.action_invoice_create()
                if not self.generate_invoice(inv_id, journals):
                    return False
                sale_id.action_done()
        return (sale_id.id, sale_id.name)
        
    @api.model
    def create(self, vals):
        result = super(sale_order, self).create(vals)
        if self._context.get('sequence_code'):
            result.name = self.env['ir.sequence'].next_by_code(self._context.get('sequence_code'))
        return result

    @api.model
    def generate_invoice(self, inv_id, journals):
        account_invoice = self.env['account.invoice'].browse(inv_id)
        if account_invoice:
            account_invoice.action_invoice_open()
            account_payment_obj = self.env['account.payment']
            for journal in journals:
                account_journal_obj = self.env['account.journal'].browse(journal.get('journal_id'))
                if account_journal_obj:

                    payment_id = account_payment_obj.with_context(from_pos=True).create({
                                               'payment_type': 'inbound',
                                               'partner_id': account_invoice.partner_id.id,
                                               'partner_type': 'customer',
                                               'journal_id': account_journal_obj.id or False,
                                               'amount': journal.get('amount'),
                                               'payment_method_id': account_journal_obj.inbound_payment_method_ids.id,
                                               'invoice_ids': [(6, 0, [account_invoice.id])],
                                               })
                    payment_id.post()
            return True
        return False

    def delivery_order(self, location_id):
        picking_id = self.picking_ids
        if picking_id:
            picking_id.write({'location_id':location_id})
        if picking_id.move_lines and location_id:
            picking_id.move_lines.write({'location_id':location_id})
        if picking_id:
            picking_id.action_confirm()
            picking_id.force_assign()
            for pack_operation in picking_id.pack_operation_product_ids:
                pack_operation.write({'qty_done':pack_operation.product_qty, 'location_id':location_id if location_id else picking_id.location_id.id})
            picking_id.do_new_transfer()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', copy=False)

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        res = super(
            SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res


class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self._context.get('from_pos'):
            super(account_abstract_payment, self)._check_amount()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
