# -*- coding: utf-8 -*-

from odoo import models,fields

class AccountTax(models.Model):
    _inherit = 'account.tax'
    tipo_afectacion_igv = fields.Many2one(
        "einvoice.catalog.07",
        string='Tipo de Afectación al IGV'
    )
    tipo_afectacion_igv_code = fields.Char(related="tipo_afectacion_igv.code")
    