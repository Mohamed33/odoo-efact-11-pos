# -*- coding: utf-8 -*-
from odoo import http

# class DashboardData(http.Controller):
#     @http.route('/dashboard_efact_retail/dashboard_efact_retail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dashboard_efact_retail/dashboard_efact_retail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dashboard_efact_retail.listing', {
#             'root': '/dashboard_efact_retail/dashboard_efact_retail',
#             'objects': http.request.env['dashboard_efact_retail.dashboard_efact_retail'].search([]),
#         })

#     @http.route('/dashboard_efact_retail/dashboard_efact_retail/objects/<model("dashboard_efact_retail.dashboard_efact_retail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dashboard_efact_retail.object', {
#             'object': obj
#         })