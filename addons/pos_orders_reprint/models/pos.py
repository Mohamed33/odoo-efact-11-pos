# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from datetime import date, datetime
from .number_to_letter import to_word
import os
import json
import pytz
from pytz import timezone

os.environ["TZ"] = "America/Lima"
        
class pos_order(models.Model):
    _inherit = 'pos.order'
    
    def return_new_order(self):
        lines = []
        for ln in self.lines:
            lines.append(ln.id)
        date_order_utc = datetime.strptime(self.date_order,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone("UTC"))
        date_order = date_order_utc.astimezone(timezone("America/Lima")).strftime("%Y-%m-%d")

        vals = {
            'amount_total': self.amount_total,
            'date_order': date_order,
            'id': self.id,
            'name': self.name,
            'partner_id': [self.partner_id.id, self.partner_id.name],
            'pos_reference': self.pos_reference,
            'state': self.state,
            'session_id': [self.session_id.id, self.session_id.name],
            'company_id': [self.company_id.id, self.company_id.name],
            'invoice_id': [self.invoice_id.id, self.invoice_id.move_name],
            'lines': lines,
        }
        os.system("echo '%s'"%(json.dumps(vals)))
        return vals


    @api.multi
    def print_pos_report(self):
    	return  self.env['report'].get_action(self, 'point_of_sale.pos_invoice_report')



    @api.multi
    def print_pos_receipt(self):
        orderlines = []
        discount = 0
        order_id = self.search([('id', '=', self.id)], limit=1)
        cliente = order_id.partner_id
        
        tipo_documento = cliente.tipo_documento if cliente else "-"
        cliente = {"name":cliente.name,"vat":cliente.vat,"tipo_doc":tipo_documento,"street":cliente.street}
        

        date_order_utc = datetime.strptime(order_id.date_order,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone("UTC"))
        date_order = date_order_utc.astimezone(timezone("America/Lima")).strftime("%Y-%m-%d")
        fecha_emision = date_order
        
        monto_letras = to_word(self.amount_total,"PEN")
        texto_qr = False
        
        footer = order_id.session_id.config_id.receipt_footer
        gravado,inafecto,exonerado,gratuito = 0,0,0,0
        if order_id.invoice_id: 
            invoice_id = order_id.invoice_id
            gravado = round(self.invoice_id.total_venta_gravado,2)
            inafecto = round(self.invoice_id.total_venta_inafecto,2)
            exonerado = round(self.invoice_id.total_venta_exonerada,2)
            gratuito = round(self.invoice_id.total_venta_gratuito,2)
            datos_qr = [self.company_id.vat,
                        invoice_id.journal_id.invoice_type_code_id,
                        invoice_id.move_name.split("-")[0],
                        invoice_id.move_name.split("-")[1],
                        str(round(invoice_id.amount_tax,2)),
                        str(round(invoice_id.amount_total,2)),
                        date_order,
                        invoice_id.partner_id.tipo_documento if invoice_id.partner_id else "-",
                        invoice_id.partner_id.vat if invoice_id.partner_id else "-"
                        ]
            os.system("echo {}".format(str(datos_qr)))
            texto_qr = "|".join(datos_qr)
        taxes = []
        if order_id.invoice_id:
            tipo_comprobante = order_id.invoice_id.invoice_type_code
            numero_comprobante = order_id.invoice_id.move_name
            comprobante = {"tipo":tipo_comprobante,"numero":numero_comprobante}
            taxes = [[tax.name,tax.amount_total,tax.tax_id.tipo_afectacion_igv.code]
                        for tax in order_id.invoice_id.tax_line_ids 
                            if tax.tax_id.tipo_afectacion_igv.code == "10"]
                            
            if len([x for x in filter(lambda t:t[2]=="10",taxes)])==0:
                taxes.append(["IGV 18%",0.0,10])

        else:
            comprobante = {"tipo":False,"numero":order_id.pos_reference}

        orderlines_obj = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
        payments = self.env['account.bank.statement.line'].search([('pos_statement_id', '=', order_id.id)])
        paymentlines = []
        subtotal = 0
        tax = 0
        change = 0
        for payment in payments:
            if payment.amount > 0:
                temp = {
                    'amount': payment.amount,
                    'name': payment.journal_id.name
                }
                paymentlines.append(temp)
            else:
                change += payment.amount
             
        for orderline in orderlines_obj.sorted(key=lambda x:x["id"]):
            new_vals = {
                    'id':orderline.id,
                    'product_id': orderline.product_id.name,
                    'qty': orderline.qty,
                    'price_unit': orderline.price_unit,
                    'discount': orderline.discount,
                }
            discount += (orderline.price_unit * orderline.qty * orderline.discount) / 100
            subtotal +=orderline.price_subtotal
            tax += (orderline.price_subtotal_incl - orderline.price_subtotal)
            orderlines.append(new_vals)
        return {
            "orderlines":orderlines,
            "discount":discount,
            "paymentlines":paymentlines,
            "change":change,
            "subtotal":subtotal,
            "tax":tax,
            "cliente":cliente,
            "comprobante":comprobante,
            "fecha_emision":fecha_emision,
            "monto_letras":monto_letras,
            "texto_qr":texto_qr,
            "footer":footer,
            "gravado":gravado,
            "inafecto":inafecto,
            "exonerado":exonerado,
            "gratuito":gratuito,
            "taxes":taxes
        }
