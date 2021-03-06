# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError,AccessError
from odoo import fields,models,api,_
import json
import time
import os
from odoo.tools.profiler import profile
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import uuid

from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode

class SaleOrder(models.Model):
    _inherit = "sale.order"

    district_id = fields.Many2one("res.country.state",related="partner_id.district_id")
    street = fields.Char("Dirección",related="partner_id.street")

class SaleAdvancePayment(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    """
    Create the invoice associated to the SO.
    :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                    (partner_invoice_id, currency)
    :param final: if True, refunds will be generated if necessary
    :returns: list of created invoices
    """
    @profile
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        os.system("echo '{} '".format("create_invoices"))
        if self.advance_payment_method == 'delivered':
            os.system("echo '{} '".format("delivered"))
            sale_orders.action_invoice_create(grouped=True)
        elif self.advance_payment_method == 'all':
            os.system("echo '{} '".format("all"))
            sale_orders.action_invoice_create(grouped=True,final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                
                so_line = sale_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                    'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
