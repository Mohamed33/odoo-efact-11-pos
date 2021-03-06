from odoo import models, fields, api


class Aceptar_letras_wizard(models.TransientModel):
    _name = 'aceptar_letras_wizard'
    _description = "Aceptar letras"

    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras')

    @api.multi
    def aceptar_letras(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)
        self.env['letra_cambio.letra'].cambiar_estado_all(records, "ACE")
