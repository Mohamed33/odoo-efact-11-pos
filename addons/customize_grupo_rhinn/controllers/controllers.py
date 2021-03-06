# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeGrupoRhinn(http.Controller):
#     @http.route('/customize_grupo_rhinn/customize_grupo_rhinn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_grupo_rhinn/customize_grupo_rhinn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_grupo_rhinn.listing', {
#             'root': '/customize_grupo_rhinn/customize_grupo_rhinn',
#             'objects': http.request.env['customize_grupo_rhinn.customize_grupo_rhinn'].search([]),
#         })

#     @http.route('/customize_grupo_rhinn/customize_grupo_rhinn/objects/<model("customize_grupo_rhinn.customize_grupo_rhinn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_grupo_rhinn.object', {
#             'object': obj
#         })