# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeIncrenta(http.Controller):
#     @http.route('/customize_increnta/customize_increnta/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_increnta/customize_increnta/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_increnta.listing', {
#             'root': '/customize_increnta/customize_increnta',
#             'objects': http.request.env['customize_increnta.customize_increnta'].search([]),
#         })

#     @http.route('/customize_increnta/customize_increnta/objects/<model("customize_increnta.customize_increnta"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_increnta.object', {
#             'object': obj
#         })