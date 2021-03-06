from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

import re


COLOR_HEX_REGEX = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
THEME_DEFAULTS = {
    'id': False,
    'inversed': False,
    'name': False
}

VARIABLES = [
    'color_primary',
    'color_optional',
    'color_success',
    'color_warning',
    'color_danger',
    'color_info',
    'color_inverse',
    'color_shade',
    'shade_mix'
]


def _check_color(value):
    if value and not COLOR_HEX_REGEX.match(value):
        raise ValidationError(_("Not a valid color"))


class Theme(models.Model):

    _name = 'adaptiv_web.theme'

    name = fields.Char(string="Name", required=True)

    color_primary = fields.Char(string="Primary color", size=7)
    color_optional = fields.Char(string="Optional color", size=7)
    color_success = fields.Char(string="Success color", size=7)
    color_warning = fields.Char(string="Warning color", size=7)
    color_danger= fields.Char(string="Danger color", size=7)
    color_info = fields.Char(string="Info color", size=7)

    color_inverse = fields.Char(string="Inverse color", size=7)
    color_shade = fields.Char(string="Shade color", size=7)

    shade_mix = fields.Integer(string="Shade mix percentage")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Theme name already exists !"),
    ]

    @api.multi
    @api.constrains('color_primary')
    def _check_color_primary(self):
        for theme in self:
            _check_color(theme.color_primary)

    @api.multi
    @api.constrains('color_optional')
    def _check_color_optional(self):
        for theme in self:
            _check_color(theme.color_optional)

    @api.multi
    @api.constrains('color_success')
    def _check_color_success(self):
        for theme in self:
            _check_color(theme.color_success)

    @api.multi
    @api.constrains('color_warning')
    def _check_color_warning(self):
        for theme in self:
            _check_color(theme.color_warning)

    @api.multi
    @api.constrains('color_danger')
    def _check_color_danger(self):
        for theme in self:
            _check_color(theme.color_danger)

    @api.multi
    @api.constrains('color_info')
    def _check_color_info(self):
        for theme in self:
            _check_color(theme.color_info)

    @api.multi
    @api.constrains('color_inverse')
    def _check_color_inverse(self):
        for theme in self:
            _check_color(theme.color_inverse)

    @api.multi
    @api.constrains('color_shade')
    def _check_color_shade(self):
        for theme in self:
            _check_color(theme.color_shade)

    @api.multi
    @api.constrains('shade_mix')
    def _check_shade_mix(self):
        for theme in self:
            if theme.shade_mix < 0 or theme.shade_mix > 100:
                raise ValidationError(_("Not a valid percentage"))

    @api.multi
    def get_less_vars(self):
        if len(self) == 0:
            return dict(THEME_DEFAULTS)

        self.ensure_one()

        theme = {
            'id': self.id,
            'name': self.name
        }

        values = self.read()

        theme.update({
            key: val
            for key, val in values[0].items()
            if key in VARIABLES and val
        })

        inverse_color = int(theme.get('color_inverse', '#000000').replace('#', '0x'), 0)
        theme['inversed'] = inverse_color > int('0x666666', 0)

        if 'color_optional' not in theme and 'color_primary' in theme:
            theme['color_optional'] = theme['color_primary']

        return theme


