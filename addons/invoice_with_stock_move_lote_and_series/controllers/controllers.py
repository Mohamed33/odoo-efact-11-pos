# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceWithStockMoveLoteAndSeries(http.Controller):
#     @http.route('/invoice_with_stock_move_lote_and_series/invoice_with_stock_move_lote_and_series/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_with_stock_move_lote_and_series/invoice_with_stock_move_lote_and_series/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_with_stock_move_lote_and_series.listing', {
#             'root': '/invoice_with_stock_move_lote_and_series/invoice_with_stock_move_lote_and_series',
#             'objects': http.request.env['invoice_with_stock_move_lote_and_series.invoice_with_stock_move_lote_and_series'].search([]),
#         })

#     @http.route('/invoice_with_stock_move_lote_and_series/invoice_with_stock_move_lote_and_series/objects/<model("invoice_with_stock_move_lote_and_series.invoice_with_stock_move_lote_and_series"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_with_stock_move_lote_and_series.object', {
#             'object': obj
#         })