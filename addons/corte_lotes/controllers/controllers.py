# -*- coding: utf-8 -*-
from odoo import http

# class CorteLotes(http.Controller):
#     @http.route('/corte_lotes/corte_lotes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/corte_lotes/corte_lotes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('corte_lotes.listing', {
#             'root': '/corte_lotes/corte_lotes',
#             'objects': http.request.env['corte_lotes.corte_lotes'].search([]),
#         })

#     @http.route('/corte_lotes/corte_lotes/objects/<model("corte_lotes.corte_lotes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('corte_lotes.object', {
#             'object': obj
#         })