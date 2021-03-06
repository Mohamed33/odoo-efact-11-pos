# -*- coding: utf-8 -*-
from odoo import http

# class CustomizeSaleOrderSelecim(http.Controller):
#     @http.route('/customize_sale_order_selecim/customize_sale_order_selecim/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_sale_order_selecim/customize_sale_order_selecim/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_sale_order_selecim.listing', {
#             'root': '/customize_sale_order_selecim/customize_sale_order_selecim',
#             'objects': http.request.env['customize_sale_order_selecim.customize_sale_order_selecim'].search([]),
#         })

#     @http.route('/customize_sale_order_selecim/customize_sale_order_selecim/objects/<model("customize_sale_order_selecim.customize_sale_order_selecim"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_sale_order_selecim.object', {
#             'object': obj
#         })