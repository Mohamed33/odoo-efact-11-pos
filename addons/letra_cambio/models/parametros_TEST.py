from odoo import fields,models,api, _
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError

class letra_cambio_parametros (models.TransientModel):
    _inherit = 'res.config.settings'

    letra_aceptada = fields.Many2one('account.account', 'Letra Aceptada')
    letra_cobranza = fields.Many2one('account.account', 'Letra en Cobranza')
    letra_descuento = fields.Many2one('account.account', 'Letra en Descuento')
    letra_pagada = fields.Many2one('account.account', 'Letra Pagada')
    letra_protestada = fields.Many2one('account.account', 'Letra Protestada')

    reconciliar = fields.Boolean('Reconciliar operaciones')

    min_age = fields.Integer( string= "Age limit")

    @api.model
    def get_values(self):
        conf = self.env['ir.config_parameter']
        return {
            'min_age': int(conf.get_param('age_verification.min_age')),
            'letra_aceptada': self.env['account.account'].search([("code","=",conf.get_param('letra_aceptada'))]),
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('age_verification.min_age', str(self.min_age))
        conf.set_param('letra_aceptada', str(self.letra_aceptada.code))


