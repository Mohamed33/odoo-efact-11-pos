# -*- coding: utf-8 -*-
from odoo import http

# class CustomerCreditLine(http.Controller):
#     @http.route('/customer_credit_line/customer_credit_line/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_credit_line/customer_credit_line/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_credit_line.listing', {
#             'root': '/customer_credit_line/customer_credit_line',
#             'objects': http.request.env['customer_credit_line.customer_credit_line'].search([]),
#         })

#     @http.route('/customer_credit_line/customer_credit_line/objects/<model("customer_credit_line.customer_credit_line"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_credit_line.object', {
#             'object': obj
#         })