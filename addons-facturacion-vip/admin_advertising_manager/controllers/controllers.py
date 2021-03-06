# -*- coding: utf-8 -*-
from odoo import http

class AdminAdvertisingManager(http.Controller):
    
    @http.route('/advertising', auth='public')
    def index_advertising(self, **kw):
        return http.request.render('admin_advertising_manager.advertising', {
        })

#     @http.route('/admin_advertising_manager/admin_advertising_manager/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('admin_advertising_manager.listing', {
#             'root': '/admin_advertising_manager/admin_advertising_manager',
#             'objects': http.request.env['admin_advertising_manager.admin_advertising_manager'].search([]),
#         })

#     @http.route('/admin_advertising_manager/admin_advertising_manager/objects/<model("admin_advertising_manager.admin_advertising_manager"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('admin_advertising_manager.object', {
#             'object': obj
#         })