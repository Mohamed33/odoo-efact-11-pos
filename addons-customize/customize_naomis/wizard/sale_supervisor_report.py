# -*- coding: utf-8 -*-
import logging
from odoo import api,models,fields
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta
log = logging.getLogger(__name__)

import functools
_WEEK_DAYS = {
    0: 'LUNES',
    1: 'MARTES',
    2: 'MIERCOLES',
    3: 'JUEVES',
    4: 'VIERNES',
    5: 'SABADO',
    6: 'DOMINGO'
}


class SaleSupervisorReport(models.TransientModel):
    _name = 'sale.supervisor.report'


    def recSaleSupervisorReportLine(self,user_id,invoices,credit,debit,supplier_ids,product_ids):
        vendedor = user_id
        lines_reduced = []

        date_start = datetime.strptime(self.date_start, "%Y-%m-%d").date()
        date_end = datetime.strptime(self.date_end, "%Y-%m-%d").date()
        date_range = [_WEEK_DAYS[date_start.weekday()]]

        for day in range(1, (date_end - date_start).days):
            date_range.append(_WEEK_DAYS[(date_start+timedelta(days=day)).weekday()])

        def filter_invoice_lines(inv,sup_ids,prod_ids,cred,deb):
            lines = []
            lines_dict = {}
            lines = inv.invoice_line_ids

            if cred or deb:
                if len(inv.referencia_nota_ids) >0:
                    for ref in inv.referencia_nota_ids:
                        lines += ref.invoice_line_ids
                    # lines += functools.reduce(lambda a,b:a.invoice_line_ids+b.invoice_line_ids,inv.referencia_nota_ids)

            if len(prod_ids):
                lines = filter(lambda x:x.product_id.id in prod_ids ,lines)

            if len(sup_ids):
                lines = filter(lambda x:x.product_id.supplier_id.id in sup_ids,lines)

            for line in lines:
                if not lines_dict.get(line.product_id.id,False):
                    lines_dict[line.product_id.id] = {"invoice_id":line.invoice_id.id,
                                                        "partner_id":line.partner_id.id,
                                                        "product_id":line.product_id.id,
                                                        "qty":line.quantity,
                                                        "price_total":round(line.price_total,3),
                                                        "discount":line.discount}
                else:
                    qty = lines_dict[line.product_id.id]["qty"]
                    price_total = round(lines_dict[line.product_id.id]["price_total"])

                    if line.invoice_id.journal_id.invoice_type_code_id in ["00","01","03","08"]:
                        lines_dict[line.product_id.id].update({
                            "qty": qty + line.quantity,
                            "price_total":  price_total + line.price_total,
                        })
                    elif line.invoice_id.journal_id.invoice_type_code_id == "07":
                        lines_dict[line.product_id.id].update({
                            "qty":round(qty - line.quantity),
                            "price_total":  price_total - line.price_total,
                        })
                    
            
            return list(lines_dict.values())
        
        lines_reduced = []
        for inv in invoices:
            lines_reduced += filter_invoice_lines(inv,supplier_ids,product_ids,credit,debit)
        
        lines_reduced= [line for line in lines_reduced if line["qty"]>0]

        monto_facturado = 0
        venta_minorista = 0
        venta_mayorista = 0
        cartera = 0
        cobertura = len(set(map(lambda x:"{}".format(x["partner_id"]),lines_reduced)))
        cantidad_comprobantes = len(set(map(lambda x:"{}".format(x["invoice_id"]),lines_reduced)))
        cartera = len(self.env['res.partner'].search([('user_id', '=', user_id), ('ruta_id.name', 'in', date_range)]))
        
        for liner in lines_reduced:
            #Total monto facturado
            monto_facturado += liner["price_total"]

            #Total venta mayorista
            venta_minorista += liner["price_total"] if liner["discount"] == 0 else 0

            #Venta minorista
            venta_mayorista += liner["price_total"] if liner["discount"] > 0 else 0

        return {
            'user_id': vendedor,
            'amount_invoiced': monto_facturado,
            'min_amount': venta_minorista,
            'max_amount': venta_mayorista,
            'cartera': cartera,
            'coverage': cobertura,
            'average': 0 if cartera == 0 else '{:0.2f}'.format((cobertura/cartera)*100) if cobertura != 0 and cartera != 0 else '0.00',
            'num_invoice': cantidad_comprobantes, #Contar solo facturas y boletas
            'sale_super_id': self.id,
            'currency_id': self.currency_id.id,
        }

    def _set_invoice_ids(self):
        if self.date_start and self.date_end:
            doc_types = ['00', '01', '03']
            
            domain = [
                ('date_invoice', '>=', self.date_start), 
                ('date_invoice', '<=', self.date_end),
                ('journal_id.invoice_type_code_id', 'in', doc_types),
                ('estado_comprobante_electronico',"!=","2_ANULADO")
            ]

            date_start = datetime.strptime(self.date_start, "%Y-%m-%d").date()
            date_end = datetime.strptime(self.date_end, "%Y-%m-%d").date()

            date_range = [_WEEK_DAYS[date_start.weekday()]]

            for day in range(1, (date_end - date_start).days):
                date_range.append(_WEEK_DAYS[(date_start+timedelta(days=day)).weekday()])

            if len(self.user_ids) > 0:
                domain.append(('user_id', 'in', self.user_ids.mapped('id')))

            invoice_ids = self.env["account.invoice"].search(domain)
            user_ids = invoice_ids.filtered(lambda i: i.user_id.login not in ['ileiva@gruponaomis.com', 'bavendano@gruponaomis.com']).mapped('user_id')
            
            self.sale_supervisor_lines = [(6,0,[])]
            SaleSupervisorReportLine = self.env['sale.supervisor.report.line']

            for u in user_ids.sorted(key=lambda u: u.name):
                user_invoices = invoice_ids.filtered(lambda  s: s.user_id.id == u.id)
                log.debug("%s",self.supplier_ids.mapped("id"))
                rec = self.recSaleSupervisorReportLine(u.id,user_invoices,self.credit_note,self.debit_note,self.supplier_ids.mapped("id"),self.product_ids.mapped("id"))
                log.error("%s",rec)
                SaleSupervisorReportLine.create(rec)
                """
                amount_invoiced = 0.0
                min_amount = 0.0
                max_amount = 0.0
                num_invoice = 0
                
                for inv in user_invoices:
                    
                    if self.supplier_ids:
                        credit_note_amount = 0
                        debit_note_amount = 0
                        for l in inv.invoice_line_ids:
                            if l.product_id.supplier_id.id in self.supplier_ids.mapped('id'):
                                amount_invoiced += l.price_total
                                if l.discount > 0.0:
                                    max_amount += l.price_total
                                else:
                                    min_amount += l.price_total

                                if len(inv.referencia_nota_ids)>0:
                                    if inv.referencia_nota_ids[0].invoice_type_code == "07" and self.credit_note:
                                        nota_lines = inv.referencia_nota_ids[0].invoice_line_ids.filtered(lambda r:r.product_id.id == l.product_id.id)
                                        if len(nota_lines) > 0:
                                            credit_note_amount += sum([l.price_total for l in nota_lines if l])
                                            amount_invoiced -= sum([l.price_total for l in nota_lines if l])
                                            if l.discount > 0.0:
                                                max_amount -= sum([l.price_total for l in nota_lines if l])
                                            else:
                                                min_amount -= sum([l.price_total for l in nota_lines if l])

                                    elif inv.referencia_nota_ids[0].invoice_type_code == "08" and self.debit_note:
                                        nota_lines = inv.referencia_nota_ids[0].invoice_line_ids.filtered(lambda r:r.product_id.id == l.product_id.id)
                                        if len(nota_lines) > 0:
                                            debit_note_amount += sum([l.price_total for l in nota_lines if l])
                                            amount_invoiced += sum([l.price_total for l in nota_lines if l])
                                            if l.discount > 0.0:
                                                max_amount += sum([l.price_total for l in nota_lines if l])
                                            else:
                                                min_amount += sum([l.price_total for l in nota_lines if l])

                        if credit_note_amount > 0:
                            num_invoice -=1
                        elif debit_note_amount > 0:
                            num_invoice += 1
                        else:
                            num_invoice += 1

                    else:
                        amount_invoiced += inv.amount_total
                        num_invoice += 1
                        if inv.total_descuentos > 0:
                            max_amount += inv.amount_total
                        else:
                            min_amount += inv.amount_total
                        
                        if len(inv.referencia_nota_ids)>0:
                            if inv.referencia_nota_ids[0].invoice_type_code == "07" and self.credit_note:
                                amount_invoiced -= inv.referencia_nota_ids[0].amount_total
                                num_invoice -= 1
                                if inv.total_descuentos > 0:
                                    max_amount -= inv.referencia_nota_ids[0].amount_total
                                else:
                                    min_amount -= inv.referencia_nota_ids[0].amount_total

                            elif inv.referencia_nota_ids[0].invoice_type_code == "08" and self.debit_note:
                                amount_invoiced += inv.referencia_nota_ids[0].amount_total
                                num_invoice += 1
                                if inv.total_descuentos > 0:
                                    max_amount += inv.referencia_nota_ids[0].amount_total
                                else:
                                    min_amount += inv.referencia_nota_ids[0].amount_total
                        
                vendors = len(self.env['res.partner'].search([('user_id', '=', u.id), ('ruta_id.name', 'in', date_range)]))
                coverage = len((set(user_invoices.mapped('partner_id.id'))))

                SaleSupervisorReportLine.create({
                    'user_id': u.id,
                    'amount_invoiced': amount_invoiced,
                    'min_amount': min_amount,
                    'max_amount': max_amount,
                    'client_portfolio': vendors,
                    'coverage': coverage,
                    'average': '{:0.2f}'.format((coverage/vendors)*100) if coverage != 0 and vendors != 0 else '0.00',
                    'num_invoice': num_invoice,
                    'sale_super_id': self.id,
                    'currency_id': self.currency_id.id
                })""" 
            
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    date_start = fields.Date(string="Fecha Inicio")
    date_end = fields.Date(string="Fecha Fin")
    user_ids = fields.Many2many('res.users', string='Vendedores')
    supplier_ids = fields.Many2many('res.partner', string='Proveedores')
    product_ids = fields.Many2many("product.product",string="Producto")
    sale_supervisor_lines = fields.One2many('sale.supervisor.report.line', 'sale_super_id', string="Lineas de Reporte") 
    currency_id = fields.Many2one('res.currency', default=_default_currency)
    credit_note = fields.Boolean(string='Nota de Credito')
    debit_note = fields.Boolean(string='Nota de Debito')

    def print_report(self):
        
        if not (self.date_start or self.date_end):
            raise ValidationError('Por favor seleccione un rango de fechas')

        self._set_invoice_ids()

        report = self.env.ref("customize_naomis.sale_supervisor_report_report")
        return report.report_action(docids=[self._ids])


class SaleSuperVisorReportLines(models.TransientModel):
    _name = 'sale.supervisor.report.line'

    user_id = fields.Many2one('res.users', string="Vendedor")
    amount_invoiced = fields.Float(string='Venta Facturada')
    min_amount = fields.Float(string='Minorista')
    max_amount = fields.Float(string='Mayorista')
    cartera = fields.Integer(string='Cartera')
    coverage = fields.Integer(string='Cobertura')
    average = fields.Float(string='% (Promedio)')
    num_invoice = fields.Integer(string='Número de Documentos')
    sale_super_id = fields.Many2one('sale.supervisor.report', string='Reporte Padre')
    currency_id = fields.Many2one('res.currency')
