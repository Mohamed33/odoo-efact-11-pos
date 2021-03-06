# -*- coding: utf-8 -*-
from . import number_to_letter
from odoo import models, api

class AccountReportInvoicea4(models.AbstractModel):
    _name = 'report.report_fact.report_invoice_document_a4'

    @api.model
    def get_report_values(self, docids, data=None):
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('account.report_invoice')
        docs = self.env["account.invoice"].browse(docids)
        
        def generate_text_qr(invoice):
            ruc_emisor = invoice.company_id.partner_id.vat
            tipo_comprobante = invoice.journal_id.invoice_type_code_id
            if(invoice.journal_id.code):
                serie = invoice.journal_id.code
            else : serie = 'B002'
            if(invoice.number):
                numero =invoice.number
            else: numero = invoice.reference
            monto_total_igv = invoice.amount_tax
            monto_total = invoice.amount_total
            fecha = invoice.date_invoice
            tipo_documento_adquirente = invoice.partner_id.catalog_06_id.code
            numero_documento = invoice.partner_id.vat
            digest_value = invoice.digest_value
            s= ruc_emisor+"|"+tipo_comprobante+"|"+serie+"|"+numero.split("-")[1]+"|"+str(monto_total_igv)+"|"+str(monto_total)+"|"+fecha+"|"+tipo_documento_adquirente+"|"+numero_documento+"|"
            return s

        return {
            'doc_ids': docids,
            'doc_model': "account.invoice",
            'docs': docs,
            'data': data,
            "generate_text_qr":generate_text_qr,
            'to_word': number_to_letter.to_word,
        }
        #return report_obj.render('account.report_invoice', docargs)


class AccountReportInvoiceticket(models.AbstractModel):
    _name = 'report.report_fact.report_invoice_document_ticket'
    _inherit = 'report.report_fact.report_invoice_document_a4'
