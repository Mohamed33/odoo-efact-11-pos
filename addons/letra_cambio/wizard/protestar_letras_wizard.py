from odoo import models, fields, api


class Aceptar_letras_wizard(models.TransientModel):
    _name = 'protestar_letras_wizard'
    _description = "Protestar letras"

    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    gastos = fields.Monetary(string='Gastos por protesto')


    @api.multi
    def protestar_letras(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)
        self.env['letra_cambio.letra'].cambiar_estado_all_gastos(records, "PRO",self.gastos)
