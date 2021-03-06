from odoo import api,models,fields
from odoo.exceptions import UserError, ValidationError
import os
from datetime import datetime

class VentaSupervisorWizard(models.TransientModel):
    _name = 'venta.supervisor.wizard'
    fecha_inicio = fields.Date("Fecha Inicio",default=fields.Date.today())
    fecha_fin = fields.Date("Fecha Fin",default=fields.Date.today())
    
    def imprimir_reporte(self):
        if self.fecha_inicio and self.fecha_fin:
            domain = [["date_invoice",">=",self.fecha_inicio],["date_invoice","<=",self.fecha_fin],["journal_id.invoice_type_code_id","in",["01","03"]]]
            comprobantes = self.env["account.invoice"].search(domain)
            report_obj = self.env.ref("customize_naomis.cn_report_supervisor_ventas")
            return report_obj.report_action(comprobantes)
        else:
            raise ValidationError("La Fecha Inicio y Fin son campos requeridos para imprimir el reporte")



class VentaSupervisorReporte(models.AbstractModel):
    _name = "report.customize_naomis.cn_report_supervisor"
    
    @api.model
    def get_report_values(self,docids,data=None):
        account_invoices_ids = self.env["account.invoice"].browse(docids)
        clientes = self.env["res.partner"].search([["ruta_id.code","=",str(datetime.now().weekday()+1).zfill(3)]])
        account_invoices_ids = account_invoices_ids.sorted(key=lambda r:r.date_invoice)
        
        if len(account_invoices_ids)>0:
            fecha_inicio = account_invoices_ids[0].date_invoice
            fecha_fin = account_invoices_ids[-1].date_invoice
        comprobantes = [{"user_id":c.user_id,"amount_total":c.amount_total,"payment_term_id":c.payment_term_id,"partner_id":c.partner_id} for c in account_invoices_ids]
        
        formas_pago = list(set([c["payment_term_id"] for c in comprobantes]))
        vendedores = list(set([c["user_id"] for c in comprobantes]))

        clientes_por_vendedor = {}
        for c in clientes:
            if c.user_id in clientes_por_vendedor:
                clientes_por_vendedor[c.user_id] += 1
            else:
                clientes_por_vendedor[c.user_id] = 0

        comprobantes_por_vendedor = {}
        for comp in comprobantes:
            if comp["user_id"] in comprobantes_por_vendedor:
                comprobantes_por_vendedor[comp["user_id"]].append(comp)
            else:
                comprobantes_por_vendedor[comp["user_id"]] = [comp]

        def get_cant_comprobantes(comprobantes):
            return len(comprobantes)
        def get_monto_total(comprobantes):
            return sum([c["amount_total"] for c in comprobantes])
        def get_cant_clientes_diferentes(comprobantes):
            return len(list(set([c["partner_id"] for c in comprobantes])))
        def get_forma_pago(comprobantes):
            monto_por_forma_pago = {}
            for fp in formas_pago:
                for c in comprobantes:
                    if c["payment_term_id"] == fp:
                        if fp in monto_por_forma_pago:
                            monto_por_forma_pago[fp] += c["amount_total"]
                        else:
                            monto_por_forma_pago[fp] = c["amount_total"]
            return monto_por_forma_pago
        
        
        records = []
        for cv in comprobantes_por_vendedor:
            comps = comprobantes_por_vendedor.get(cv,[])
            cartera = clientes_por_vendedor.get(cv,0)
            cobertura = get_cant_clientes_diferentes(comps)
            cantidad_documentos = get_cant_comprobantes(comps)
            porcentaje = 0
            if cartera != 0:
                porcentaje = cobertura*100.0/cartera
            record = {
                'company_name':self.env["res.users"].browse(self.env.uid).company_id.name,
                "codigo": cv.partner_id.ref if cv.partner_id.ref else "0" ,
                "vendedor_nombre":cv.partner_id.name if cv.partner_id.name else "-",
                "total_venta":get_monto_total(comps),
                "mayorista":"",
                "minorista":"",
                "cartera":cartera,
                "cobertura":cobertura,
                "porcentaje":str(round(porcentaje,2))+" %",
                "kilos":"",
                "cantidad_documentos": cantidad_documentos,
            }
            record.update(get_forma_pago(comps))
            records.append(record)
        return {
            "records":records,
            "formas_pago":formas_pago,
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_fin,
            "fecha_hoy":fields.Date.today()
        }   