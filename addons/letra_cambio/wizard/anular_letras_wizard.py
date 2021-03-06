from odoo import models, fields, api


class Anular_letras_wizard(models.TransientModel):
    _name = 'anular_letras_wizard'
    _description = "Anular letras"

    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras')

    @api.multi
    def anular_letras(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)
        self.env['letra_cambio.letra'].cambiar_estado_all(records, "ANU")
