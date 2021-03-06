# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeFelifibras(http.Controller):
#     @http.route('/customize_felifibras/customize_felifibras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_felifibras/customize_felifibras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_felifibras.listing', {
#             'root': '/customize_felifibras/customize_felifibras',
#             'objects': http.request.env['customize_felifibras.customize_felifibras'].search([]),
#         })

#     @http.route('/customize_felifibras/customize_felifibras/objects/<model("customize_felifibras.customize_felifibras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_felifibras.object', {
#             'object': obj
#         })