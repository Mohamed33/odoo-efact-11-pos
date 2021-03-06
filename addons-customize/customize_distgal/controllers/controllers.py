# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeDistgal(http.Controller):
#     @http.route('/customize_distgal/customize_distgal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_distgal/customize_distgal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_distgal.listing', {
#             'root': '/customize_distgal/customize_distgal',
#             'objects': http.request.env['customize_distgal.customize_distgal'].search([]),
#         })

#     @http.route('/customize_distgal/customize_distgal/objects/<model("customize_distgal.customize_distgal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_distgal.object', {
#             'object': obj
#         })