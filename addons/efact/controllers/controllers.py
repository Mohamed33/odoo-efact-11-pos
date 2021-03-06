# -*- coding: utf-8 -*-
from odoo import http

class Efact(http.Controller):
    @http.route('/efact/efact/',type="json" , auth='public')
    def index(self, **kw):
        return {"msg":"Hello, world"}

#     @http.route('/efact/efact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('efact.listing', {
#             'root': '/efact/efact',
#             'objects': http.request.env['efact.efact'].search([]),
#         })

#     @http.route('/efact/efact/objects/<model("efact.efact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('efact.object', {
#             'object': obj
#         })
