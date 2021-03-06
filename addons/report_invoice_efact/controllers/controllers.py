# -*- coding: utf-8 -*-
from odoo import http

# class ReportInvoiceEfact(http.Controller):
#     @http.route('/report_invoice_efact/report_invoice_efact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_invoice_efact/report_invoice_efact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_invoice_efact.listing', {
#             'root': '/report_invoice_efact/report_invoice_efact',
#             'objects': http.request.env['report_invoice_efact.report_invoice_efact'].search([]),
#         })

#     @http.route('/report_invoice_efact/report_invoice_efact/objects/<model("report_invoice_efact.report_invoice_efact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_invoice_efact.object', {
#             'object': obj
#         })