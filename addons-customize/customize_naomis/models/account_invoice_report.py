# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

class ResMarca(models.Model):
    _name = "res.cn.marca"
    name = fields.Char("Nombre")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    supplier_id = fields.Many2one("res.partner",string="Proveedor")
    marca_id = fields.Many2one("res.cn.marca",string="Marca")

class ProductProduct(models.Model):
    _inherit = "product.product"
    supplier_id = fields.Many2one("res.partner",related="product_tmpl_id.supplier_id",string="Proveedor")
    marca_id = fields.Many2one("res.cn.marca",string="Marca")

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    supplier_id = fields.Many2one("res.partner",related="product_id.supplier_id",string="Proveedor")

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"
    supplier_id = fields.Many2one("res.partner",string="Proveedor")

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.supplier_id as supplier_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", pt.supplier_id as supplier_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", pt.supplier_id"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    supplier_id = fields.Many2one("res.partner",related="product_id.supplier_id",string="Proveedor")

class SaleReport(models.Model):
    _inherit = "sale.report"    
    supplier_id = fields.Many2one("res.partner",string="Proveedor")

    def _select(self):
        return super(SaleReport, self)._select() + ", t.supplier_id as supplier_id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", t.supplier_id"
    """
    def _from(self):
        return super(SaleReport, self)._from() + " left join res_partner partner2 on (p.supplier_id = partner2.id)"
    """