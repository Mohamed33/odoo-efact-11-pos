# -*- coding: utf-8 -*-
from odoo import http

# class Tipocambio(http.Controller):
#     @http.route('/tipocambio/tipocambio/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tipocambio/tipocambio/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tipocambio.listing', {
#             'root': '/tipocambio/tipocambio',
#             'objects': http.request.env['tipocambio.tipocambio'].search([]),
#         })

#     @http.route('/tipocambio/tipocambio/objects/<model("tipocambio.tipocambio"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tipocambio.object', {
#             'object': obj
#         })