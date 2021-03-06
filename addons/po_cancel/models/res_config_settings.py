# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    cancel_delivery_order_for_po = fields.Boolean(string="Cancel Delivery Order?")
    cancel_invoice_for_po = fields.Boolean(string='Cancel Invoice?')

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            cancel_delivery_order_for_po=self.env.user.company_id.cancel_delivery_order_for_po ,
            cancel_invoice_for_po = self.env.user.company_id.cancel_invoice_for_po
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company_id=self.env.user.company_id
        company_id.cancel_invoice_for_po = self.cancel_invoice_for_po
        company_id.cancel_delivery_order_for_po = self.cancel_delivery_order_for_po
