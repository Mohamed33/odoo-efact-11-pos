# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeGrupoblas(http.Controller):
#     @http.route('/customize_grupoblas/customize_grupoblas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_grupoblas/customize_grupoblas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_grupoblas.listing', {
#             'root': '/customize_grupoblas/customize_grupoblas',
#             'objects': http.request.env['customize_grupoblas.customize_grupoblas'].search([]),
#         })

#     @http.route('/customize_grupoblas/customize_grupoblas/objects/<model("customize_grupoblas.customize_grupoblas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_grupoblas.object', {
#             'object': obj
#         })