# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeMultilogistica(http.Controller):
#     @http.route('/customize_multilogistica/customize_multilogistica/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_multilogistica/customize_multilogistica/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_multilogistica.listing', {
#             'root': '/customize_multilogistica/customize_multilogistica',
#             'objects': http.request.env['customize_multilogistica.customize_multilogistica'].search([]),
#         })

#     @http.route('/customize_multilogistica/customize_multilogistica/objects/<model("customize_multilogistica.customize_multilogistica"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_multilogistica.object', {
#             'object': obj
#         })