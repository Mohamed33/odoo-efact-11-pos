# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeNaomis(http.Controller):
#     @http.route('/customize_naomis/customize_naomis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_naomis/customize_naomis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_naomis.listing', {
#             'root': '/customize_naomis/customize_naomis',
#             'objects': http.request.env['customize_naomis.customize_naomis'].search([]),
#         })

#     @http.route('/customize_naomis/customize_naomis/objects/<model("customize_naomis.customize_naomis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_naomis.object', {
#             'object': obj
#         })