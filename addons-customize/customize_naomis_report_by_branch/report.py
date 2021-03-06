from odoo import models,fields,api,_
import pandas as pd
import numpy as np
import io
from datetime import datetime,timedelta
import base64
from io import BytesIO
import json
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class ResBranch(models.Model):
    _inherit = "res.branch"

    def send_report(self,branch,days):
        branch_obj = self.env["res.branch"].sudo().search([("name","=",branch)])
        template_obj = self.env.ref("customize_naomis_report_by_branch.template_mail_report_by_branch")
        ir_attachment = self.env["ir.attachment"]
        fecha_inicio = (datetime.now()-timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
        fecha_fin = (datetime.now()-timedelta(days=days)).strftime("%Y-%m-%d 23:59:59")

        if branch_obj.exists():
            report = self.env['ir.actions.report']._get_report_from_name("customize_report_by_branch.report_by_branch_xlsx")
            # report_obj = self.env.ref("customize_naomis_report_by_branch.report_xlsx")
            data = {"fecha_inicio":fecha_inicio,
                    "fecha_fin":fecha_fin,
                    "branch_id":branch_obj.id,
                    "supplier_ids":branch_obj.supplier_ids.ids if branch_obj.supplier_ids else []}
            # _logger.info(data)
            xlsx = report.with_context(self.env.context).render_xlsx([], data=data)[0]
            xlsx_b64 = base64.b64encode(xlsx)
            name = "Reporte de ventas {} {}".format(fecha_inicio,fecha_fin)
            attachment = {
                "name":"Reporte XLSX",
                "datas":xlsx_b64,
                "datas_fname":"{}.xlsx".format(name),
                "res_model":"res.branch",
                "type":"binary",
                "mimetype":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
            # _logger.info(attachment)
            att = self.env["ir.attachment"].create(attachment)
            # _logger.info(att)
            template_obj.attachment_ids = [(6,0,[att.id])]
            # _logger.info(xlsx)    
            mail_id = template_obj.send_mail(branch_obj.id)
            self.env["mail.mail"].browse(mail_id).send()
            self.env.cr.commit()
            template_obj.attachment_ids = [(3,0,att.id)]


class WizardReportByBranch(models.TransientModel):
    _name = 'wizard.report.by.branch'
    _description = "Wizard Report By Branch"
    fecha_inicio = fields.Date("Fecha de Inicio",default=fields.Date.today())
    fecha_fin = fields.Date("Fecha Fin",default=fields.Date.today())
    branch_id = fields.Many2one("res.branch",string="Sucursal",default=lambda self:self.env.user.branch_id.id)

    # def send_mail(self,branch):
    #     branch_obj = self.env["res.branch"].sudo().search([("name","=",branch)])
    #     if branch_obj.exists():
    #         report = self.env['ir.actions.report']._get_report_from_name("customize_report_by_branch.report_by_branch_xlsx")
    #         data = {"fecha_inicio":datetime.now().strftime("%Y-%m-%d 00:00:00"),
    #                 "fecha_fin":datetime.now().strftime("%Y-%m-%d 23:59:59"),
    #                 "branch_id":branch_id,
    #                 "supplier_ids":self.branch_id.supplier_ids.ids if self.branch_id.supplier_ids else []}
    #         xlsx = report.with_context(self.env.context).render_xlsx([], data=data)[0]

    def btn_generate_xlsx(self):
        report_obj = self.env.ref("customize_naomis_report_by_branch.report_xlsx")
        fecha_inicio = "{} 00:00:00".format(self.fecha_inicio)
        fecha_fin = "{} 23:59:00".format(self.fecha_fin)
        # _logger.info(report_obj.report_action([],{"fecha_inicio":self.fecha_inicio,"fecha_fin":self.fecha_fin,"branch_id":self.branch_id.id if self.branch_id else False,"supplier_ids":self.branch_id.supplier_ids.ids if self.branch_id.supplier_ids else []}))
        return report_obj.report_action([],{"fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"branch_id":self.branch_id.id if self.branch_id else False,"supplier_ids":self.branch_id.supplier_ids.ids if self.branch_id.supplier_ids else []})

class ReportByBranch(models.AbstractModel):
    _name = "report.customize_report_by_branch.report_by_branch_xlsx"
    _inherit = "report.report_xlsx.abstract"

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

    def get_employees(self,branch_id):
        employee_objs = self.env["res.users"].search([("branch_id","=",branch_id),("active","in",[True,False])])
        employees = []
        if len(employee_objs) > 0:
            employees = employee_objs.mapped(lambda r:{
                        "Cod_persona":r.partner_id.ref,
                        "Nombre":r.partner_id.name,
                        "DNI o RUC":r.partner_id.vat,
                        "N° Telefono":r.partner_id.mobile,
                        "ESTADO":r.state
                    })
        return employees

    def get_products(self,supplier_ids):
        product_objs = self.env["product.product"].search([("supplier_id","in",supplier_ids),("active","in",[True,False])])
        products = []
        if len(product_objs) > 0 :
            products = product_objs.mapped(lambda r:{
                        "Marca":r.marca_id.name if r.marca_id else "-",
                        "Categoría":r.categ_id.name if r.categ_id else "-",
                        "cod_articulo":r.default_code,
                        "descripción de articulo":r.name,
                        "Formato":"",
                        "UN/PQ":"",
                    })
        return products

    def get_customers(self,branch_id):
        customers_objs = self.env["res.partner"].search([("branch_id","=",branch_id),("active","in",[True,False])])
        customers = []
        if len(customers_objs) > 0:
            customers = customers_objs.mapped(lambda r:{
                        "ZONA":r.zona_id.name if r.zona_id else "-",
                        "RUTA":r.ruta_id.name if r.ruta_id else "-",
                        "COD_CLIENTE":r.ref,
                        "NOMBRE DE CLIENTE":r.name,
                        "DIRECCION":r.street,
                        "DOCUMENTO":r.vat,
                        "GIRO NEGOCIO":r.tipo_establecimiento_id.name if r.tipo_establecimiento_id else "-",
                        "TELEFONO":r.mobile,
                        "SEGMENTO":r.segmento,
                        "COORD X":r.longitud,
                        "COORD Y":r.latitud,
                        "ESTADO":r.state
                    })
        return customers
    
    def get_sales_order(self,supplier_ids,fecha_inicio,fecha_fin):
        sale_order_objs = self.env["sale.order.line"].search([("product_id.supplier_id","in",supplier_ids),
                                                            ("order_id.date_order",">=",fecha_inicio),
                                                            ("order_id.date_order","<=",fecha_fin)])
        # _logger.info(sale_order_objs)     
        sale_orders = []
        if len(sale_order_objs) > 0:                                           
            sale_orders = sale_order_objs.mapped(lambda r:{
                            "COMPAÑÍA":r.company_id.name,
                            "SUCURSAL":r.company_id.name,
                            "FECHA":datetime.strptime(r.order_id.date_order,"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"),	
                            "PROVEDOR":r.branch_id.name if r.branch_id else "-",
                            "SUPERVISOR":"-",
                            "COD_VENDEDOR":r.order_id.user_id.name if r.order_id.user_id else "-",	
                            "RUTA":";".join([ruta for ruta in r.order_id.ruta_ids.mapped(lambda r: r.name)]),
                            "COD_CLIENTE":r.order_id.partner_id.ref,
                            "CODIGO ARTICULO":r.product_id.default_code,
                            "UNIDADES_ARTICULO":r.product_uom.factor_inv,
                            "TIPO VENTA":r.order_id.state,
                            "CAJAS O PAQUETES":r.product_uom_qty,
                            "SOLES":r.price_total
                        })
        return sale_orders

    def get_state_invoice(self,line):
        product_id = line.product_id
        invoice_id = line.invoice_id
        notas_ids = invoice_id.referencia_nota_ids
        if len(notas_ids) > 0:
            nota_line_product_ids = notas_ids.mapped(lambda r:r.invoice_line_ids)
            devolucion = nota_line_product_ids.filtered(lambda r:r.product_id==line.product_id and r.invoice_id.state in ["open","paid"])

            if devolucion.quantity  == line.quantity:
                return {"estado":"DEVOLUCIÓN TOTAL","sustento":"|".join(["{}:{}".format(d.invoice_id.move_name,d.invoice_id.sustento_nota) for d in devolucion])}
            elif devolucion.quantity  < line.quantity:
                return {"estado":"DEVOLUCIÓN PARCIAL","sustento":"|".join(["{}:{}".format(d.invoice_id.move_name,d.invoice_id.sustento_nota) for d in devolucion])}
        
        return {"estado":"EMITIDO","sustento":"-"}

    def get_guia(self,line):
        invoice_id = line.invoice_id
        guia_remision_ids = invoice_id.guia_remision_ids
        placa = "-"
        chofer = "-"
        if len(guia_remision_ids) > 0:
            transportista_id = guia_remision_ids[0].transportista_id
            vehicle_id = guia_remision_ids[0].vehicle_id
            if transportista_id:
                chofer = transportista_id.name if transportista_id.name else "-"
            if vehicle_id:
                placa = vehicle_id.numero_placa if vehicle_id.numero_placa else "-"

        return {"chofer":chofer,"placa":placa}

    def get_invoices(self,supplier_ids,fecha_inicio,fecha_fin):
        invoice_objs = self.env["account.invoice.line"].search([("product_id.supplier_id","in",supplier_ids),
                                                                ("invoice_id.date_invoice",">=",fecha_inicio),
                                                                ("invoice_id.date_invoice","<=",fecha_fin),
                                                                ("invoice_id.state","in",["open","paid"])])
        def get_ruta(partner):
            if partner.ruta_id:
                return partner.ruta_id.name if partner.ruta_id.name else "-"
            return "-"
        invoices = []
        if len(invoice_objs) > 0:
            invoices = invoice_objs.mapped(lambda r:{
                            "COMPAÑÍA":r.company_id.name,
                            "SUCURSAL":r.company_id.name,	
                            "FECHA":datetime.strptime(r.invoice_id.date_invoice,"%Y-%m-%d").strftime("%d/%m/%Y"),
                            "DOC DE VENTA":r.invoice_id.move_name,
                            "SUPERVISOR":"",
                            "PLACA":self.get_guia(r).get("placa"),
                            "CHOFER":self.get_guia(r).get("chofer"),
                            "PROVEDOR":r.product_id.supplier_id.name if r.product_id.supplier_id else "-",
                            "Cod Vendedor":r.invoice_id.user_id.name,
                            "Ruta":get_ruta(r.invoice_id.partner_id),
                            "Cod_Cliente":r.invoice_id.partner_id.ref,
                            "CODIGO ARTICULO":r.product_id.default_code,
                            "Unidades x Articulo":r.product_id.uom_id.factor_inv,
                            "Tipo de Venta":"Boni" if r.no_onerosa else "Venta",
                            "Cajas o Paquetes":"",
                            "Soles Imp Bruto":r.price_total,
                            "ESTADO DOC":self.get_state_invoice(r).get("estado"),
                            "motivo de rechazo":self.get_state_invoice(r).get("sustento")
                        })
        return invoices

    def generate_xlsx_report(self, workbook, data, records):
        fecha_inicio = data.get("fecha_inicio",False)
        fecha_fin = data.get("fecha_fin",False)
        branch_id = data.get("branch_id",False)
        supplier_ids = data.get("supplier_ids",False)
        # _logger.info(branch_id)
        # _logger.info(supplier_ids)
        # _logger.info(fecha_inicio)
        # _logger.info(fecha_fin)
        employees = self.get_employees(branch_id)
        products = self.get_products(supplier_ids)
        customers = self.get_customers(branch_id)
        sale_orders = self.get_sales_order(supplier_ids,fecha_inicio,fecha_fin)
        invoices = self.get_invoices(supplier_ids,fecha_inicio,fecha_fin)

        df_employees = pd.DataFrame(employees,columns=["Cod_persona","Nombre","DNI o RUC","N° Telefono","ESTADO"])
        df_products = pd.DataFrame(products,columns=["Marca","Categoría","cod_articulo","descripción de articulo","Formato","UN/PQ"])
        df_customers = pd.DataFrame(customers,columns=["ZONA","RUTA","COD_CLIENTE","NOMBRE DE CLIENTE","DIRECCION","DOCUMENTO","GIRO NEGOCIO","TELEFONO","SEGMENTO","COORD X","COORD Y","ESTADO"])
        df_sales_order = pd.DataFrame(sale_orders,columns=["COMPAÑÍA","SUCURSAL","FECHA","PROVEDOR","SUPERVISOR","COD_VENDEDOR","RUTA","COD_CLIENTE","CODIGO ARTICULO","UNIDADES_ARTICULO","TIPO VENTA","CAJAS O PAQUETES","SOLES"])
        df_invoices = pd.DataFrame(invoices,columns=["COMPAÑÍA","SUCURSAL","FECHA","DOC DE VENTA","SUPERVISOR","PLACA","CHOFER","PROVEDOR","Cod Vendedor","Ruta","Cod_Cliente","CODIGO ARTICULO","Unidades x Articulo","Tipo de Venta","Cajas o Paquetes","Soles Imp Bruto","ESTADO DOC","motivo de rechazo"])

        df_employees.to_excel(workbook,sheet_name='Tabla Vendedor Persona')
        df_products.to_excel(workbook,sheet_name='Tabla Codigo Articulo')
        df_customers.to_excel(workbook,sheet_name='Tabla Maestro de Clientes')
        df_sales_order.to_excel(workbook,sheet_name='Reporte de PreVenta')
        df_invoices.to_excel(workbook,sheet_name='Reporte Venta')