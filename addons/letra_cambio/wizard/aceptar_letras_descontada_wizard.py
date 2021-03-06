from odoo import models, fields, api


class Aceptar_letras_descontada_wizard(models.TransientModel):
    _name = 'aceptar_letras_descontada_wizard'
    _description = "Aceptar letras descontadas"

    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras descontadas')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    gastos = fields.Float(string='Gastos por descuento')

    @api.multi
    def aceptar_letras_descontadas(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)
        self.env['letra_cambio.letra'].cambiar_estado_all_gastos(records, "DEA", self.gastos)
