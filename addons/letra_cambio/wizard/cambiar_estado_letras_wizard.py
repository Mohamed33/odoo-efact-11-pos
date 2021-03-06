from odoo import models, fields, api


class Wizard_cambiar_estado(models.TransientModel):
    _name = 'cambiar_estado_letras_wizard'
    _description = "Cambiar estado de letras"

    def _get_letras(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []


    letra_ids = fields.Many2many('letra_cambio.letra', default=_get_letras, string='Letras')
    #number = fields.Char('número' , related= 'letra_ids.number',store=True, readonly=True, copy=False )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ACE', 'Aceptada'),
        ('COB', 'Cobranza'),
        ('DES', 'Descuento'),
        ('PRO', 'Protestada'),
        ('ANU', 'Anulada'),
        ('PAG', 'Pagado'),
    ], string='Estado final')

    @api.multi
    def cambiar_estado_letras(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['letra_cambio.letra'].browse(active_ids)
        self.env['letra_cambio.letra'].cambiar_estado_all(records,self.state)

