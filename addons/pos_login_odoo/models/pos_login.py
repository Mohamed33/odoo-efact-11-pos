# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class res_users(models.Model):
    _inherit = 'res.users'

    pos_config = fields.Many2one('pos.config', string="Point of Sale")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
