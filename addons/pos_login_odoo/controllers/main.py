# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
#from openerp.addons.web.controllers.main import Home
from odoo.addons.website.controllers.main import Website
        
class PosWebsiteLogin(Website):

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(PosWebsiteLogin, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                if request.env['res.users'].browse(request.uid).pos_config:
                    redirect = '/pos/web'
                else:
                    redirect = '/web?' + request.httprequest.query_string
            elif request.env['res.users'].browse(request.uid).pos_config:
                redirect = '/pos/web'
            else:
                redirect = '/'
            return http.redirect_with_hash(redirect)
        return response


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
