# -*- coding: utf-8 -*-
from odoo import http

# class ThemeFullstack(http.Controller):
#     @http.route('/theme_fullstack/theme_fullstack/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/theme_fullstack/theme_fullstack/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('theme_fullstack.listing', {
#             'root': '/theme_fullstack/theme_fullstack',
#             'objects': http.request.env['theme_fullstack.theme_fullstack'].search([]),
#         })

#     @http.route('/theme_fullstack/theme_fullstack/objects/<model("theme_fullstack.theme_fullstack"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('theme_fullstack.object', {
#             'object': obj
#         })
