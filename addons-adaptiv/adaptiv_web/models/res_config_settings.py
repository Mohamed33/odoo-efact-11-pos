from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    theme_id = fields.Many2one(related='company_id.theme_id', string="Theme")
    svg_logo = fields.Binary(related='company_id.svg_logo')
    png_logo = fields.Binary(related='company_id.svg_logo')
    svg_logo_inverse = fields.Binary(related='company_id.svg_logo_inverse')
    png_logo_inverse = fields.Binary(related='company_id.png_logo_inverse')

    debrand_name = fields.Char(related='company_id.debrand_name')
    debrand_favicon = fields.Binary(related='company_id.debrand_favicon')
