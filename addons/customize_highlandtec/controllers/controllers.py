# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeHighlandtec(http.Controller):
#     @http.route('/customize_highlandtec/customize_highlandtec/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_highlandtec/customize_highlandtec/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_highlandtec.listing', {
#             'root': '/customize_highlandtec/customize_highlandtec',
#             'objects': http.request.env['customize_highlandtec.customize_highlandtec'].search([]),
#         })

#     @http.route('/customize_highlandtec/customize_highlandtec/objects/<model("customize_highlandtec.customize_highlandtec"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_highlandtec.object', {
#             'object': obj
#         })