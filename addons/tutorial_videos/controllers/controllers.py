# -*- coding: utf-8 -*-
from odoo import http

# class TutorialVideos(http.Controller):
#     @http.route('/tutorial_videos/tutorial_videos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tutorial_videos/tutorial_videos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tutorial_videos.listing', {
#             'root': '/tutorial_videos/tutorial_videos',
#             'objects': http.request.env['tutorial_videos.tutorial_videos'].search([]),
#         })

#     @http.route('/tutorial_videos/tutorial_videos/objects/<model("tutorial_videos.tutorial_videos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tutorial_videos.object', {
#             'object': obj
#         })