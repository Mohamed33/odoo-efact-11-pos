# -*- coding: utf-8 -*-
from odoo import http

# class Oim-admin(http.Controller):
#     @http.route('/oim-admin/oim-admin/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oim-admin/oim-admin/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oim-admin.listing', {
#             'root': '/oim-admin/oim-admin',
#             'objects': http.request.env['oim-admin.oim-admin'].search([]),
#         })

#     @http.route('/oim-admin/oim-admin/objects/<model("oim-admin.oim-admin"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oim-admin.object', {
#             'object': obj
#         })