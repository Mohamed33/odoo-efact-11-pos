# -*- coding: utf-8 -*-
from odoo import fields,models,api

class ProductUom(models.Model):
    _inherit = "product.uom"
    code=fields.Char(string="Codigo")
    description=fields.Char(string="Descripcion")
