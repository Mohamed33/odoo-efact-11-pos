# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo
from odoo.http import route, request
from odoo.addons.auth_quick_master.tools.build_redirection import build_redirection
from time import sleep


class SaasController(odoo.http.Controller):
    @route('/saas/auth-to-build/<int:build_id>', type='http', auth='user')
    def auth_to_build(self, build_id=None, **kwargs):
        if not build_id:
            return False
        build_url = request.env['saas.db'].browse(build_id).get_url() + '/auth_quick/login?build_login=admin'
        return build_redirection(build_url)

    @route('/empezar', auth='public')
    def wizard(self, **kwargs):
        return request.render('saas.wizard_template')

    @route('/crear_instancia', type='http', auth='public', method=["POST"], csrf=False, website=True)
    def crear_instancia(self, **post):
        nombre = post.get("nombre")

        instancia = request.env["saas.template"].sudo().create({'name' : nombre})
        instancia.with_delay().crear_database()


    @route('/instalar', type='http', auth='public', method=["POST"], csrf=False, website=True)
    def instalar(self, **post):
        nombre = post.get("nombre")

        instancia = request.env["saas.template"].sudo().search([('name','=' ,nombre)])
        modulos =[]
        modulos.extend(['crm'])
        modulos.extend(['project'])
        instancia.with_delay().install_modulo_lista(modulos)

    @route('/get_status', type='http', auth='public', method=["POST"], csrf=False, website=True)
    def status(self, **post):
        nombre = post.get("nombre")
        instancia = request.env["saas.template"].sudo().search([('name', '=', nombre)])
        return instancia.get_status()