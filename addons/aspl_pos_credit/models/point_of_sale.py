# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_credit = fields.Boolean('Credit Management')
    receipt_balance = fields.Boolean('Display Balance info in Receipt')
    print_ledger = fields.Boolean('Print Credit Statement')
    pos_journal_id = fields.Many2one('account.journal', string='Select Journal')

    @api.model
    def get_outstanding_info(self):
        return True

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _calc_remaining(self):
        for partner in self:
            data = self.env['account.invoice'].get_outstanding_info(partner.id)
            amount = []
            amount_data = 0.00
            total = 0.00
            for pay in data['content']:
                amount_data =  pay['amount']
                amount.append(amount_data)
            for each_amount in amount:
                total += each_amount
            partner.remaining_credit_amount = total

    remaining_credit_amount = fields.Float(compute="_calc_remaining", string="Remaining Amount",
                                           store=False,readonly=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: