# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeLeoarte(http.Controller):
#     @http.route('/customize_leoarte/customize_leoarte/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_leoarte/customize_leoarte/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_leoarte.listing', {
#             'root': '/customize_leoarte/customize_leoarte',
#             'objects': http.request.env['customize_leoarte.customize_leoarte'].search([]),
#         })

#     @http.route('/customize_leoarte/customize_leoarte/objects/<model("customize_leoarte.customize_leoarte"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_leoarte.object', {
#             'object': obj
#         })