from odoo import api, fields, models
class ResCompany(models.Model):
    _inherit = "res.company"

    cancel_delivery_order_for_po = fields.Boolean(string="Cancel Delivery Order?")
    cancel_invoice_for_po = fields.Boolean(string='Cancel Invoice?')
