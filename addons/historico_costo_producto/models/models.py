# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    reference = fields.Char(related="invoice_id.reference")
    date_invoice = fields.Date(related="invoice_id.date_invoice")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_view_listar_historico_precio(self):
        product_objs = self.env["product.product"].sudo().search([("product_tmpl_id","=",self.id)])
        product_ids = [product_obj.id for product_obj in product_objs]
        invoice_line_ids = self.env["account.invoice.line"].search([["product_id","in",product_ids],["invoice_type","=","in_invoice"]])
        return {
            "type":"ir.actions.act_window",
            "name":"Histórico de precios costo facturados",
            "res_model":"account.invoice.line",
            "view_mode":"tree,form",
            "views":[[request.env.ref("historico_costo_producto.view_tree_invoice_line_compra").id,"tree"]],
            "domain":[["id","in",[inv.id for inv in invoice_line_ids]]],
            "target":"self"
        }
    