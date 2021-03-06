# -*- coding: utf-8 -*-
from odoo import http

# class LetraCambio(http.Controller):
#     @http.route('/letra_cambio/letra_cambio/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/letra_cambio/letra_cambio/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('letra_cambio.listing', {
#             'root': '/letra_cambio/letra_cambio',
#             'objects': http.request.env['letra_cambio.letra_cambio'].search([]),
#         })

#     @http.route('/letra_cambio/letra_cambio/objects/<model("letra_cambio.letra_cambio"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('letra_cambio.object', {
#             'object': obj
#         })