# -*- coding: utf-8 -*-
from odoo import http

# class Kardex(http.Controller):
#     @http.route('/kardex/kardex/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kardex/kardex/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kardex.listing', {
#             'root': '/kardex/kardex',
#             'objects': http.request.env['kardex.kardex'].search([]),
#         })

#     @http.route('/kardex/kardex/objects/<model("kardex.kardex"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kardex.object', {
#             'object': obj
#         })