# -*- coding: utf-8 -*-
from odoo import http

# class JsreportEfact(http.Controller):
#     @http.route('/jsreport_efact/jsreport_efact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jsreport_efact/jsreport_efact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jsreport_efact.listing', {
#             'root': '/jsreport_efact/jsreport_efact',
#             'objects': http.request.env['jsreport_efact.jsreport_efact'].search([]),
#         })

#     @http.route('/jsreport_efact/jsreport_efact/objects/<model("jsreport_efact.jsreport_efact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jsreport_efact.object', {
#             'object': obj
#         })