# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import base64 
import os 

class AccountInvoice(models.Model): 
    
    _inherit = ['account.invoice']

    pdf_invoice_file = fields.Binary("Comprobante")
    

    def action_print_invoice_jsreport(self):
        endpoint = self.company_id.jsreport_endpoint
        username = self.company_id.jsreport_username
        password = self.company_id.jsreport_password
        short_id = self.company_id.jsreport_template_invoice_short_id
        if not endpoint:
            UserError("El Endpoint de JsReport esta vacío")
        if not username:
            UserError("No se puede conectar al API de JSReport debido a que el Campo Username esta vacío")
        if not password:
            UserError("No se puede conectar al API de JSReport debido a que el Campo Password esta vacío")
        if not short_id:
            UserError("El Short Id del template esta vacío")

        data = json.loads(self.json_comprobante)
        data["documento"]["digestValue"]=self.digest_value
        payload ={"template":{"shortid":short_id},"data":data}
        payload = json.dumps(payload)
        cred = username+":"+password
        cred = cred.encode("utf-8")
        
        Authorization = base64.b64encode(cred)
        
        headers = {
            'content-type': "application/json",
            'authorization': b'Basic ' +Authorization,
            }

        response = requests.request("POST", endpoint, data=payload, headers=headers)
        self.pdf_invoice_file = base64.b64encode(response.content)

        url = "/web/content?model=account.invoice&field=pdf_invoice_file&filename_field=%s&id=%s"%(self.number+".pdf",str(self.id))
        return {
             'type' : 'ir.actions.act_url',
             'url': url,
             'target': 'new',
        }