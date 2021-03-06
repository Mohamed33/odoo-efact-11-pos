from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class Pagar_letras_wizard(models.TransientModel):
    _name = 'pagar_letras_wizard'
    _description = "Pagar letras"


    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras')

    currency_id = fields.Many2one('res.currency', string='Moneda')
    gastos = fields.Monetary(string='Gastos por cobranza libre')

    @api.multi
    def pagar_letras(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)

        self.env['letra_cambio.letra'].cambiar_estado_all_gastos(records, "PAG",self.gastos)
