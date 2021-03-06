# -*- coding: utf-8 -*-
from odoo import http

# class LetraDeCambio(http.Controller):
#     @http.route('/letra_de_cambio/letra_de_cambio/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/letra_de_cambio/letra_de_cambio/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('letra_de_cambio.listing', {
#             'root': '/letra_de_cambio/letra_de_cambio',
#             'objects': http.request.env['letra_de_cambio.letra_de_cambio'].search([]),
#         })

#     @http.route('/letra_de_cambio/letra_de_cambio/objects/<model("letra_de_cambio.letra_de_cambio"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('letra_de_cambio.object', {
#             'object': obj
#         })