# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class res_company(models.Model):
    _inherit = "res.company"

    account_template = fields.Selection([
            ('a4', 'A4'),
            ('ticket', 'Ticket'),
        ], 'Tamaño documento' , default='a4')


class account_invoice(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True

        if self.company_id.account_template == 'a4':
            return self.env.ref('report_fact.custom_account_invoices_a4').report_action(self)

        if self.company_id.account_template == 'ticket':
            return self.env.ref('report_fact.custom_account_invoices_ticket').report_action(self)


