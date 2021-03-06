# -*- coding: utf-8 -*-
from odoo import http

# class ReportComprobantesEfact(http.Controller):
#     @http.route('/report_comprobantes_efact/report_comprobantes_efact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_comprobantes_efact/report_comprobantes_efact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_comprobantes_efact.listing', {
#             'root': '/report_comprobantes_efact/report_comprobantes_efact',
#             'objects': http.request.env['report_comprobantes_efact.report_comprobantes_efact'].search([]),
#         })

#     @http.route('/report_comprobantes_efact/report_comprobantes_efact/objects/<model("report_comprobantes_efact.report_comprobantes_efact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_comprobantes_efact.object', {
#             'object': obj
#         })