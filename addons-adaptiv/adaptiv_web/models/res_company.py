from odoo import api, models, fields, _


class ResCompany(models.Model):

    _inherit = 'res.company'

    svg_logo = fields.Binary("Logo (svg)", attachment=True,
        help="This field holds the SVG file used as a logo.")
    svg_logo_inverse = fields.Binary("Logo inverse (svg)", attachment=True,
        help="This field holds the SVG file used as an inverse logo. "
        "The inverse logo is displayed in the sidebar.")
    png_logo = fields.Binary("Logo (png)", attachment=True,
        help="This field holds the PNG image used as a logo.")
    png_logo_inverse = fields.Binary("Logo inverse (png)", attachment=True,
        help="This field holds the PNG image used as an inverse logo. "
        "This logo is displayed in the sidebar.")

    theme_id = fields.Many2one('adaptiv_web.theme', default=lambda self: self.env.ref('adaptiv_web.theme_default', raise_if_not_found=False))

    debrand_name = fields.Char(string="Debrand Name", default="Odoo")
    debrand_favicon = fields.Binary(string="Debrand Favicon", help="This field holds the image used to display a favicon instead of the default one.")

    @api.model
    def get_current(self):
        user = self.env.user
        if not user or user.company_id is False:
            # Get superuser
            user = self.sudo().env.user
        return user.company_id
