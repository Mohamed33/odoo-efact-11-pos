# -*- coding: utf-8 -*-
from odoo import fields,models,api 

class ProductTemplate(models.Model):
    _inherit = "product.template"
    detail = fields.Html("Detalle")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    detail_html = fields.Html("Detalle")

    @api.multi
    @api.onchange("product_id")
    def _onchange_product_id(self):
        for record in self:
            record.detail_html = record.product_id.detail
    
    def edit_sale_order_line(self):
        self.ensure_one()
        view = self.env.ref('customize_felifibras.view_sale_order_line')
        
        return {
            "type":"ir.actions.act_window",
            "view_type":"form",
            "res_model":"sale.order.line",
            "target":"new",
            'res_id': self.id,
            'views': [(view.id, 'form')]
        }