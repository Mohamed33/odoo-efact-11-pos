# -*- coding: utf-8 -*-
from odoo import http

# class SnippetPopupformButton(http.Controller):
#     @http.route('/snippet_popupform_button/snippet_popupform_button/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/snippet_popupform_button/snippet_popupform_button/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('snippet_popupform_button.listing', {
#             'root': '/snippet_popupform_button/snippet_popupform_button',
#             'objects': http.request.env['snippet_popupform_button.snippet_popupform_button'].search([]),
#         })

#     @http.route('/snippet_popupform_button/snippet_popupform_button/objects/<model("snippet_popupform_button.snippet_popupform_button"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('snippet_popupform_button.object', {
#             'object': obj
#         })