from odoo import models,fields,api,_
import pandas as pd
import numpy as np
import io

from io import BytesIO
import json
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class WizardPosOrderReport(models.TransientModel):
    _name = 'wizard.pos.order.report'
    fecha_inicio = fields.Date("Fecha de Inicio")
    fecha_fin = fields.Date("Fecha Fin")
    pos_config_id = fields.Many2one("pos.config",string="PDV")
    
    def btn_generate_xlsx(self):
        report_obj = self.env.ref("report_invoice_efact.pos_order_report_xlsx")
        return report_obj.report_action([],{"fecha_inicio":self.fecha_inicio,"fecha_fin":self.fecha_fin,"config_id":self.pos_config_id.id})
    
class PartnerXlsx(models.AbstractModel):
    _name = 'report.report_invoice_efact.wizard_report_pos'
    _inherit = 'report.report_xlsx.abstract'

    def create_xlsx_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        file_data = BytesIO()
        #workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        workbook = pd.ExcelWriter(file_data, engine='xlsxwriter')
        self.generate_xlsx_report(workbook, data, objs)
        #workbook.close()
        workbook.save()
        file_data.seek(0)
        return file_data.read(), 'xlsx'

    def generate_xlsx_report(self, workbook, data, records):
        fecha_inicio = data.get("fecha_inicio",False)
        fecha_fin = data.get("fecha_fin",False)
        domain = []
        if fecha_fin:
            domain.append(["statement_id.date","<=",fecha_fin])
        if fecha_inicio:
            domain.append(["statement_id.date",">=",fecha_inicio])

        statement_ids = self.env["account.bank.statement.line"].search(domain)

        def get_invoice(statement):
            if statement:
                if statement.invoice_id:
                    return statement.invoice_id.number if statement.invoice_id.number else ""
            return ""
        def get_session(statement):
            return statement.name
        statements = [
            [   
                get_session(s.statement_id),
                s.date[:10],
                "VENTA" if s.pos_statement_id else "SALIDA DE DINERO" if s.amount<0 else "INGRESO DE DINERO",
                (s.pos_statement_id.name + (" | "+get_invoice(s.pos_statement_id) if get_invoice(s.pos_statement_id) else  "")) if s.pos_statement_id else s.name,
                get_invoice(s.pos_statement_id),
                s.name,
                s.partner_id.name if s.partner_id else "",
                s.journal_id.name if s.journal_id else "",
                s.amount
            ]
            for s in statement_ids
        ]
        df_states = pd.DataFrame(statements,columns=["Sesion","Fecha","Tipo","Referencia","invoice",'name', 'Cliente',"journal_id","Monto"])
        table_1 = pd.pivot_table(df_states,columns=["Sesion","Fecha","Tipo","Cliente","Referencia"],values=["Monto"],aggfunc=[np.sum])
        table_2 = pd.pivot_table(df_states,columns=["Sesion","Fecha","Tipo"],values=["Monto"],aggfunc=[np.sum])
        
        table_1.to_excel(workbook, sheet_name='Detalle de POS')
        table_2.to_excel(workbook, sheet_name='Resumen de POS')