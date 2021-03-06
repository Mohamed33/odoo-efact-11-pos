from odoo import fields, models,api 
from odoo.exceptions import UserError, ValidationError
from odoo.tools.profiler import profile

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    def action_invoice_open(self):
        journals_no_disponibles = []
        pos_config_active_ids = self.env["pos.config"].sudo().search([["active","=",True]])
        for config in pos_config_active_ids:
            journals_no_disponibles += config.invoice_journal_ids
        
        pos_order_id = self.env["pos.order"].search([["name","=",self.origin]])
        if pos_order_id:
            if not pos_order_id.from_pos and self.journal_id in journals_no_disponibles:
                raise UserError("La serie seleccionada no se encuentra disponible debido a que se está usando en un Punto de Venta.")

        return super(AccountInvoice, self).action_invoice_open()