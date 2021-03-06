# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError,AccessError
from odoo import fields,models,api,_

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='none',
                                        readonly=True, states={'draft': [('readonly', False)]},
                                        default=lambda self: self.env.user, copy=False)
    
    @profile
    @api.model
    def create(self, vals):
        os.system("echo 'Log de Creación de factura desde efact'")
        return super(AccountInvoice,self.with_context(tracking_disable=True)).create(vals)
        
    @api.multi
    def _track_subtype(self, init_values):
        return False
        self.ensure_one()
        if 'state' in init_values and self.state == 'paid' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_paid'
        elif 'state' in init_values and self.state == 'open' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_validated'
        elif 'state' in init_values and self.state == 'draft' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_created'
        return super(AccountInvoice, self)._track_subtype(init_values)
