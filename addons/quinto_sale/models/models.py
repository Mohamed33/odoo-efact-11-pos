# -*- coding: utf-8 -*-

from odoo import models, fields, api

"""
class QuintoMarca(models.Model):
    _name = "quinto.marca"
    name = fields.Char("Nombre")
    description = fields.Char("Descripción")


class ProductProduct(models.Model):
    _inherit = "product.product"
    marca_id = fields.Many2one("quinto.marca",string="Marca")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    marca_id = fields.Many2one("quinto.marca",string="Marca")
    margen = fields.Float("Márgen de Ganancia (%)")

    @api.onchange('standard_price','margen')
    def compute_list_price(self):
        self.list_price=(1+float(self.margen/100.0))*self.standard_price
"""