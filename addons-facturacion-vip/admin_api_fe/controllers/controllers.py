# -*- coding: utf-8 -*-
from odoo import http

# class AdminApiFe(http.Controller):
#     @http.route('/admin_api_fe/admin_api_fe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/admin_api_fe/admin_api_fe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('admin_api_fe.listing', {
#             'root': '/admin_api_fe/admin_api_fe',
#             'objects': http.request.env['admin_api_fe.admin_api_fe'].search([]),
#         })

#     @http.route('/admin_api_fe/admin_api_fe/objects/<model("admin_api_fe.admin_api_fe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('admin_api_fe.object', {
#             'object': obj
#         })