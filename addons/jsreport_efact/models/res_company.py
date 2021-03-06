# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    
    _inherit = ['res.company']

    jsreport_username = fields.Char("Username")
    jsreport_password = fields.Char("Password")
    jsreport_endpoint = fields.Char("Endpoint")
    jsreport_template_invoice_short_id = fields.Char("Factura Short ID")

        
# class jsreport_efact(models.Model):
#     _name = 'jsreport_efact.jsreport_efact'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100