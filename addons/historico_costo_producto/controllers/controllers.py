# -*- coding: utf-8 -*-
from odoo import http

# class HistoricoCostoProducto(http.Controller):
#     @http.route('/historico_costo_producto/historico_costo_producto/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/historico_costo_producto/historico_costo_producto/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('historico_costo_producto.listing', {
#             'root': '/historico_costo_producto/historico_costo_producto',
#             'objects': http.request.env['historico_costo_producto.historico_costo_producto'].search([]),
#         })

#     @http.route('/historico_costo_producto/historico_costo_producto/objects/<model("historico_costo_producto.historico_costo_producto"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('historico_costo_producto.object', {
#             'object': obj
#         })