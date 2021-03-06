# -*- coding: utf-8 -*-
from odoo import http

# class QuintoSale(http.Controller):
#     @http.route('/quinto_sale/quinto_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quinto_sale/quinto_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('quinto_sale.listing', {
#             'root': '/quinto_sale/quinto_sale',
#             'objects': http.request.env['quinto_sale.quinto_sale'].search([]),
#         })

#     @http.route('/quinto_sale/quinto_sale/objects/<model("quinto_sale.quinto_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quinto_sale.object', {
#             'object': obj
#         })