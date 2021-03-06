# -*- coding: utf-8 -*-
from . import number_to_letter
from odoo import models, api


class AccountReportInvoiceWithPayments(models.AbstractModel):
    _name = 'report.account.report_invoice_with_payments'

    @api.model
    def get_report_values(self, docids, data=None):
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('account.report_invoice')
        docs = self.env["account.invoice"].browse(docids)
        
        def generate_text_qr(invoice):
            ruc_emisor = invoice.company_id.partner_id.vat
            tipo_comprobante = invoice.journal_id.invoice_type_code_id
            serie = invoice.journal_id.code
            numero = invoice.number
            monto_total_igv = invoice.amount_tax
            monto_total = invoice.amount_total
            fecha = invoice.date_invoice
            tipo_documento_adquirente = invoice.partner_id.tipo_documento if invoice.partner_id.tipo_documento else "-"
            numero_documento = invoice.partner_id.vat if invoice.partner_id.vat else "-"
            digest_value = invoice.digest_value if invoice.digest_value else "-"
            s= ruc_emisor+"|"+tipo_comprobante+"|"+serie+"|"+numero.split("-")[1]+"|"+str(monto_total_igv)+"|"+str(monto_total)+"|"+fecha+"|"+tipo_documento_adquirente+"|"+numero_documento+"|"+digest_value
            return s

        return {
            'doc_ids': docids,
            'doc_model': "account.invoice",
            'docs': docs,
            'data': data,
            "generate_text_qr":generate_text_qr,
            'to_word': number_to_letter.to_word,
        }


class AccountReportInvoice(models.AbstractModel):
    _name = 'report.account.report_invoice'

    @api.model
    def get_report_values(self, docids, data=None):
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('account.report_invoice')
        docs = self.env["account.invoice"].browse(docids)
        
        def generate_text_qr(invoice):
            ruc_emisor = invoice.company_id.partner_id.vat
            tipo_comprobante = invoice.journal_id.invoice_type_code_id
            serie = invoice.journal_id.code
            numero = invoice.number
            monto_total_igv = invoice.amount_tax
            monto_total = invoice.amount_total
            fecha = invoice.date_invoice
            tipo_documento_adquirente = invoice.partner_id.tipo_documento if invoice.partner_id.tipo_documento else "-"
            numero_documento = invoice.partner_id.vat if invoice.partner_id.vat else "-" 
            digest_value = invoice.digest_value if invoice.digest_value else "-"
            s= ruc_emisor+"|"+tipo_comprobante+"|"+serie+"|"+numero.split("-")[1]+"|"+str(monto_total_igv)+"|"+str(monto_total)+"|"+fecha+"|"+tipo_documento_adquirente+"|"+numero_documento+"|"+digest_value
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