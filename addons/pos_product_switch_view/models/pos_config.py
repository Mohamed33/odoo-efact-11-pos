# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_product_view = fields.Selection([('product_form_view','Form View'),('product_list_view','List View')],string='Product Screen',default='product_form_view')

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
