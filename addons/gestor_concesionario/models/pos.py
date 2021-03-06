
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PosConfigConcesionario(models.Model):
    _inherit = "pos.config"

    company_con_id = fields.Many2one(
        'res.partner', string='Company',
        domain=[('es_empresa','=',True)], required=True)


class PosSessionConcesionario(models.Model):
    _inherit = "pos.session"

    company_con_id = fields.Many2one(
        'res.partner', string='Company',
        domain=[('es_empresa','=',True)], required=True, readonly=True, nullable=True)

    @api.model
    def create(self, values):
        config_id = values.get('config_id') or self.env.context.get('default_config_id')
        if not config_id:
            raise UserError(_("You should assign a Point of Sale to your session."))
        pos_config = self.env['pos.config'].browse(config_id)
        if not pos_config.company_con_id:
            return UserError(_("This Pos Configuration does\'nt have any company"))
        #company_con_id = self.env['res.partner'].browse(pos_config.company_con_id.id)
        values.update({
            'company_con_id': pos_config.company_con_id.id
        })
        res = super(PosSessionConcesionario, self).create(values)
        return res
