# -*- coding: utf-8 -*-
from odoo import http

# class ReportFact(http.Controller):
#     @http.route('/report_fact/report_fact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_fact/report_fact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_fact.listing', {
#             'root': '/report_fact/report_fact',
#             'objects': http.request.env['report_fact.report_fact'].search([]),
#         })

#     @http.route('/report_fact/report_fact/objects/<model("report_fact.report_fact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_fact.object', {
#             'object': obj
#         })