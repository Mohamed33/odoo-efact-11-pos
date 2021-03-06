# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from datetime import date, datetime
import os
import json

class pos_order(models.Model):
    _inherit = 'pos.order'

    def send_mail(self,email):
        if self.invoice_id:
            email_temp = self.invoice_id.partner_id.email
            self.invoice_id.partner_id.email = email
            template = self.env.ref("account.email_template_edi_invoice")
            mail_id = self.env['mail.template'].browse(template.id).send_mail(self.invoice_id.id)
            mail = self.env["mail.mail"].browse(mail_id)
            mail.send()
            self.invoice_id.partner_id.email = email_temp
    
    def return_new_order(self):
        lines = []
        for ln in self.lines:
            lines.append(ln.id)

        vals = {
            'amount_total': self.amount_total,
            'date_order': self.date_order,
            'id': self.id,
            'name': self.name,
            'partner_id': [self.partner_id.id, self.partner_id.name],
            'pos_reference': self.pos_reference,
            'state': self.state,
            'session_id': [self.session_id.id, self.session_id.name],
            'company_id': [self.company_id.id, self.company_id.name],
            'lines': lines,
        }
        os.system("echo '%s'"%(json.dumps(vals)))
        return vals
    
    def return_new_order_line(self):
       
       orderlines = self.env['pos.order.line'].search([('order_id.id','=', self.id)])
       
       final_lines = []
       #for ln in self.lines:
           #lines.append(ln.id)
       #print "lllllllllllllllliiiiiiiiiiinnnnnnnnnnnnnneeeeeeeessssssssssssss",orderlines
       
       for l in orderlines:
           vals1 = {
                'discount': l.discount,
                'id': l.id,
                'order_id': [l.order_id.id, l.order_id.name],
                'price_unit': l.price_unit,
                'product_id': [l.product_id.id, l.product_id.name],
                'qty': l.qty,
           }
           final_lines.append(vals1)
           
       return final_lines   


    
