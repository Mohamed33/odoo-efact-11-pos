# -*- coding: utf-8 -*-
from odoo import http

# class EfullstackCourseManagement(http.Controller):
#     @http.route('/efullstack_course_management/efullstack_course_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/efullstack_course_management/efullstack_course_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('efullstack_course_management.listing', {
#             'root': '/efullstack_course_management/efullstack_course_management',
#             'objects': http.request.env['efullstack_course_management.efullstack_course_management'].search([]),
#         })

#     @http.route('/efullstack_course_management/efullstack_course_management/objects/<model("efullstack_course_management.efullstack_course_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('efullstack_course_management.object', {
#             'object': obj
#         })