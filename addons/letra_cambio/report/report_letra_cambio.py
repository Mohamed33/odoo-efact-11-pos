#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from . number_to_letter import to_word

class report_letra_cambio(models.AbstractModel):
    _name = 'report.letra_cambio.letra_cambio_template'


    @api.model
    def get_report_values(self, docids, data=None):
        letras = self.env['letra_cambio.letra'].browse(docids)
        company = self.env['res.company'].search([('id','=','1')])
        return {
            'doc_ids': docids,
            'doc_model': 'letra_cambio.letra',
            'docs': letras,
            'data': data,
            'to_word' : to_word,
            'company' : company
        }
