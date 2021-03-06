# -*- coding: utf-8 -*-
from odoo import http

# class AwsSnsSms(http.Controller):
#     @http.route('/aws_sns_sms/aws_sns_sms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aws_sns_sms/aws_sns_sms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aws_sns_sms.listing', {
#             'root': '/aws_sns_sms/aws_sns_sms',
#             'objects': http.request.env['aws_sns_sms.aws_sns_sms'].search([]),
#         })

#     @http.route('/aws_sns_sms/aws_sns_sms/objects/<model("aws_sns_sms.aws_sns_sms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aws_sns_sms.object', {
#             'object': obj
#         })