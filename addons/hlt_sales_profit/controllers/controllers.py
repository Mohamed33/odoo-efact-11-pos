# -*- coding: utf-8 -*-
from odoo import http

# class HltSalesProfit(http.Controller):
#     @http.route('/hlt_sales_profit/hlt_sales_profit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hlt_sales_profit/hlt_sales_profit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hlt_sales_profit.listing', {
#             'root': '/hlt_sales_profit/hlt_sales_profit',
#             'objects': http.request.env['hlt_sales_profit.hlt_sales_profit'].search([]),
#         })

#     @http.route('/hlt_sales_profit/hlt_sales_profit/objects/<model("hlt_sales_profit.hlt_sales_profit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hlt_sales_profit.object', {
#             'object': obj
#         })