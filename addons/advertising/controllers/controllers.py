# -*- coding: utf-8 -*-
from odoo import http

# class Advertising(http.Controller):
#     @http.route('/advertising/advertising/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/advertising/advertising/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('advertising.listing', {
#             'root': '/advertising/advertising',
#             'objects': http.request.env['advertising.advertising'].search([]),
#         })

#     @http.route('/advertising/advertising/objects/<model("advertising.advertising"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('advertising.object', {
#             'object': obj
#         })