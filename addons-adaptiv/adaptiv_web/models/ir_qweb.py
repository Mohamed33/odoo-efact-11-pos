import ast
from urllib.parse import urlparse
from lxml import html
from werkzeug import urls
import json

from odoo import models, api, tools
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.assetsbundle import AssetsBundle
from odoo.modules.module import get_resource_path
from odoo.tools import pycompat


THEME_SEP = '.adaptivtheme.'


class IrQWeb(models.AbstractModel):

    _inherit = 'ir.qweb'

    def _get_asset(self, xmlid, options, css=True, js=True, debug=False, async=False, values=None):
        values = values or {}
        # Prefix css assets if a theme is used. The render method
        # will restore the original xml_id. By changing the xml_id
        # Odoo will create seperate orm caches and files.
        if css and values.get('theme') and values['theme']['id'] is not False:
            # We need to prefix instead of suffix the xmlid
            # since odoo will otherwise see the id as a split asset
            xmlid = '%s%s%s' % (values['theme']['id'], THEME_SEP, xmlid)
        res = super(IrQWeb, self)._get_asset(xmlid, options, css=css, js=js, debug=debug, async=async, values=values)
        return res

    @api.model
    def get_current_company(self):
        if not request or not hasattr(request, '__current_company'):
            company = self.env['res.company'].sudo().get_current()
            if not request:
                return company
            setattr(request , '__current_company', company)
        return getattr(request, '__current_company')

    @api.model
    def get_theme(self):
        # Uncomment the line below if upgrading from version <= 107
        # Comment the line below after the database has been upgraded

        #return { inversed: False, id: False }

        if not (request and request.debug == 'assets'):
            theme_id = False
            if 'theme' in request.httprequest.args:
                theme = request.httprequest.args.get('theme')
                try:
                    theme = int(theme)
                except ValueError:
                    theme_id = self.env['adaptiv_web.theme'].sudo().search([('name', 'ilike', theme)], limit=1)
                else:
                    theme_id = self.env['adaptiv_web.theme'].sudo().browse([theme]).exists()
            else:
                theme_id = self.get_current_company().theme_id

            return theme_id.get_less_vars()

    @api.model
    def get_debrand_options(self):
        company_id = self.get_current_company()
        return {
            'title': company_id.debrand_name,
            'favicon_url': company_id.debrand_favicon and '/web/image/res.company/%s/debrand_favicon/' % company_id.id
        }

    @api.model
    def get_themes(self):
        return self.env['adaptiv_web.theme'].sudo().search([])

    @api.model
    def render(self, id_or_xml_id, values=None, **options):
        if isinstance(id_or_xml_id, str):
            theme_parts = id_or_xml_id.split(THEME_SEP)
            if len(theme_parts) == 2:
                id_or_xml_id = theme_parts[1]

        values = values or {}
        # Since this variable will be available in every template
        # prefix it with adaptiv_
        values.update({
            'theme': self.get_theme(),
            'debrand': self.get_debrand_options(),
            'get_available_themes': self.get_themes,
            # Backward compatibility
            'adaptiv_get_theme': self.get_theme,
            'adaptiv_get_themes': self.get_themes
        })

        return super(IrQWeb, self).render(id_or_xml_id, values=values, **options)
