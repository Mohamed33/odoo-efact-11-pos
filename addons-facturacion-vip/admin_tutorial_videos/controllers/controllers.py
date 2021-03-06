# -*- coding: utf-8 -*-
from odoo import http

# class AdminTutorialVideos(http.Controller):
#     @http.route('/admin_tutorial_videos/admin_tutorial_videos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/admin_tutorial_videos/admin_tutorial_videos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('admin_tutorial_videos.listing', {
#             'root': '/admin_tutorial_videos/admin_tutorial_videos',
#             'objects': http.request.env['admin_tutorial_videos.admin_tutorial_videos'].search([]),
#         })

#     @http.route('/admin_tutorial_videos/admin_tutorial_videos/objects/<model("admin_tutorial_videos.admin_tutorial_videos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('admin_tutorial_videos.object', {
#             'object': obj
#         })