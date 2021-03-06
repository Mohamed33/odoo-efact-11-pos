# -*- coding: utf-8 -*-
from odoo import http

# class Ple(http.Controller):
#     @http.route('/ple/ple/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ple/ple/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ple.listing', {
#             'root': '/ple/ple',
#             'objects': http.request..env['ple.ple'].search([]),
#         })

#     @http.route('/ple/ple/objects/<model("ple.ple"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ple.object', {
#             'object': obj
#         })