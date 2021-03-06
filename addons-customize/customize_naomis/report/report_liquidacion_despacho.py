from odoo import api,models,fields
from odoo.exceptions import UserError, ValidationError
import os
from datetime import datetime



class LiquidacionDespachoReport(models.AbstractModel):
    _name = "report.customize_naomis.cn_liquidacion_despacho_report"

    @api.model
    def get_report_values(self,docids,data=None):
        comprobantes_por_vendedor = {}
        account_invoice_ids = self.env["account.invoice"].browse(docids)
        account_invoice_ids = account_invoice_ids.sorted(key=lambda r:r.date_invoice)
        if len(account_invoice_ids)>0:
            fecha_inicio = account_invoice_ids[0].date_invoice
            fecha_fin = account_invoice_ids[-1].date_invoice

        for ai in account_invoice_ids:
            if ai.user_id in comprobantes_por_vendedor:
                comprobantes_por_vendedor[ai.user_id].append(ai)
            else:
                comprobantes_por_vendedor[ai.user_id] = [ai]
        
        comprobantes_por_vendedor = [[k,comprobantes_por_vendedor[k]] for k in comprobantes_por_vendedor]
        return {
            'company_name':self.env["res.users"].browse(self.env.uid).company_id.name,
            "registros":comprobantes_por_vendedor,
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_fin,
            "fecha_hoy":fields.Date.today()
        }

