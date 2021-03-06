from odoo import fields,models,api, _
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError

class letra_cambio_parametros (models.TransientModel):
    _inherit = 'res.config.settings'

    cuenta_por_cobrar = fields.Char('Cuenta por cobrar')
    letra_aceptada = fields.Char('Letra Aceptada')
    letra_cobranza = fields.Char('Letra en Cobranza')
    letra_descuento = fields.Char('Letra en Descuento')
    letra_descontada_aceptada = fields.Char('Letra desc. aceptada')
    letra_protestada = fields.Char('Letra Protestada')
    #gastos_financieros = fields.Char('Gastos Financieros')
    gasto_descontada_aceptada = fields.Char('Gastos por descuento aceptada')
    gasto_cobranza_libre = fields.Char('Gastos por cobranza libre')
    gasto_protestada = fields.Char('Gastos por protesto')


    reconciliar = fields.Boolean('Reconciliar operaciones')


    @api.model
    def get_values(self):
        conf = self.env['ir.config_parameter']
        return {
            'cuenta_por_cobrar' : str(conf.get_param('cuenta_por_cobrar')),
            'letra_aceptada': str(conf.get_param('letra_aceptada')),
            'letra_cobranza': str(conf.get_param('letra_cobranza')),
            'letra_descuento': str(conf.get_param('letra_descuento')),
            'letra_protestada': str(conf.get_param('letra_protestada')),
            'letra_descontada_aceptada': str(conf.get_param('letra_descontada_aceptada')),
            'gasto_descontada_aceptada': str(conf.get_param('gasto_descontada_aceptada')),
            'gasto_cobranza_libre': str(conf.get_param('gasto_cobranza_libre')),
            'gasto_protestada': str(conf.get_param('gasto_protestada')),

        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']

        conf.set_param('cuenta_por_cobrar', str(self.cuenta_por_cobrar))
        conf.set_param('letra_aceptada', str(self.letra_aceptada))
        conf.set_param('letra_cobranza', str(self.letra_cobranza))
        conf.set_param('letra_descuento', str(self.letra_descuento))
        conf.set_param('letra_protestada', str(self.letra_protestada))
        conf.set_param('letra_descontada_aceptada', str(self.letra_descontada_aceptada))
        conf.set_param('gasto_descontada_aceptada', str(self.gasto_descontada_aceptada))
        conf.set_param('gasto_cobranza_libre', str(self.gasto_cobranza_libre))
        conf.set_param('gasto_protestada', str(self.gasto_protestada))


