# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    duracion = fields.Float(string="Duración")
    es_curso = fields.Boolean(strng="Es un Curso")

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    duracion = fields.Float(string="Duración")
    es_curso = fields.Boolean(strng="Es un Curso")