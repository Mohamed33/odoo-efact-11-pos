# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from datetime import timedelta,datetime
from random import choice
import csv 
import io
from io import StringIO
import os

def generador_codigo():
    longitud = 4
    valores = "0123456789abcdefghijklmnopqrstuvwxyz"
    p = ""
    p = p.join([choice(valores) for i in range(longitud)])
    return p

class ResPartner(models.Model):
    _inherit = "res.partner"
    #activo = fields.Boolean("Activo")
    es_comensal = fields.Boolean("Es un Comensal")
    empresa_id = fields.Many2one("res.partner")
    es_empresa = fields.Boolean("Es una Empresa")
    programacion_ids = fields.One2many("ca.programacion","empresa_id")
    tipo=fields.Selection(selection=[("interno","Interno"),("externo","Externo")],default="interno")

    identificador = fields.Char("identificador")
    codigocomensal = fields.Char("codigocomensal")

    @api.constrains("empresa_id")
    def _select_empresa_partner(self):
        if self.es_comensal and not self.empresa_id:
            raise ValidationError("Ustéd debe seleccionar una empresa")
        if not self.empresa_id.es_empresa:
            raise ValidationError("Debe seleccionar una empresa")

    comensal_ids = fields.One2many("res.partner","empresa_id")
    total_comensales = fields.Integer("Total de Comensales",compute="_total_comensales")


    @api.onchange("registration_name")
    def _get_name(self):
        for record in self:
            self.name=record.registration_name

    @api.multi
    @api.depends("comensal_ids")
    def _total_comensales(self):
        for record in self:
            record.total_comensales =len(record.comensal_ids)

    codigo = fields.Char("Código")
    tipo_comensal = fields.Char("Tipo de Comensal")
    cargo = fields.Char("Cargo")
    area = fields.Char("area")

    filename = fields.Char("Nombre de Archivo")
    comensales_csv = fields.Binary("Comensales CSV")
    ultimo_reporte = fields.Binary("Último Reporte")


    def btn_view_reporte_ventas(self):
        return {
            "type":"ir.actions.act_window",
            "target":"new",
            "views":[[False,"form"]],
            "res_model":"view_report_venta",
            "context":{"default_empresa_id":self.id},
            "name":"Reporte de Ventas"
        }

    def reporte_ventas(self,fecha_inicio=False,fecha_fin=False):
        name = "Reporte de Concesion alimentaria"+" "+(fecha_inicio if fecha_inicio else "")+" - "+(fecha_fin if fecha_fin else "")+".xls"
        writer = pd.ExcelWriter("/mnt/extra-addons/" + name)
        metodo_pago_ids=self.env["account.journal"].sudo().search([["type","in",["cash","bank"]]])
        export = False
        comensal_ids=[cm.vat for cm in self.comensal_ids]

        #domain2=[["partner_id.vat","in",comensal_ids],["session_id.company_con_id","=",self.id]]
        domain2=[["session_id.company_con_id","=",self.id]]
        
        #domain=[["partner_id","in",comensal_ids],["journal_id","=",mp.id]]
        if fecha_inicio:
            #domain.append(["date_order", ">=", fecha_inicio])
            domain2.append(["date_order", ">=", fecha_inicio])
        if fecha_fin:
            #domain.append(["date_order", "<=", fecha_fin])
            domain2.append(["date_order", "<=", fecha_fin])
        #pago_ids=self.env["account.bank.statement.line"].sudo().search(domain)
        pos_order=self.env["pos.order"].sudo().search(domain2)
        
        for mp in metodo_pago_ids:
            
            """
            lines =[{"cliente":po.partner_id.name,
                     "fecha":po.date_order[0:10],
                     "productos":"-".join([l.product_id.name+"[Cant:"+str(l.qty)+"]"+"[PU:"+str(l.price_unit)+"]" for l in po.lines])
                     } for po in pos_order if len(po.statement_ids)>0 if po.statement_ids[0].journal_id.id==mp.id ]
            """
            header =["tipo", "tipo_comensal","dni","codigo","cliente","pedido","comprobante","vendedor","fecha","fecha_completa","producto","cantidad","precio_unitario","total","vendedor","referencia_de_pedido","metodo de pago","monto"]
            lines_2=[
                [
                    po.partner_id.tipo,
                    po.partner_id.tipo_comensal,
                    po.partner_id.vat,
                    po.partner_id.codigo,
                    po.partner_id.name,
                    po.name,
                    str(po.invoice_id.move_name if po.invoice_id else " - "),
                    po.user_id.name,
                    datetime.strftime(datetime.strptime(po.date_order,"%Y-%m-%d %H:%M:%S")-timedelta(hours=5), '%Y-%m-%d'),
                    #po.date_order[0:10] if po.date_order else "",
                    datetime.strptime(po.date_order,"%Y-%m-%d %H:%M:%S")-timedelta(hours=5),
                    line.product_id.name,
                    line.qty,
                    line.price_unit,
                    line.qty*line.price_unit,
                    po.user_id.name,
                    po.pos_reference,
                    stat_id.journal_id.name,
                    po.amount_total
                ] for po in pos_order
                    for line in po.lines
                        for stat_id in po.statement_ids[0:1]
                            if stat_id.journal_id.id == mp.id
            ]
            header_pagos=["tipo","tipo_comensal","dni","codigo","cliente","fecha","fecha_completa","metodo pago","monto"]
            pagos=[
                [
                    po.partner_id.tipo,
                    po.partner_id.tipo_comensal,
                    po.partner_id.vat,
                    po.partner_id.codigo,
                    po.partner_id.name,
                    #po.date_order[0:10] if po.date_order else "",
                    datetime.strftime(datetime.strptime(po.date_order,"%Y-%m-%d %H:%M:%S")-timedelta(hours=5), '%Y-%m-%d'),
                    datetime.strptime(po.date_order,"%Y-%m-%d %H:%M:%S")+timedelta(hours=-5),
                    stat_id.journal_id.id,
                    po.amount_total
                ] for po in pos_order
                    for stat_id in po.statement_ids[0:1]
                        if stat_id.journal_id.id == mp.id
            ]
            """
            pagos=[
                {
                    "cliente":pago.partner_id.name,
                    "dni":pago.partner_id.vat,
                    "codigo":pago.partner_id.codigo,
                    "tipo_comensal":pago.partner_id.tipo_comensal,
                    "monto":pago.amount,
                    "fecha":pago.date
                } for pago in pago_ids]
            """


            #lines_df=json_normalize(lines)

            if len(pagos)>0:
                #pagos_df = json_normalize(pagos)
                pagos_df = pd.DataFrame(pagos,columns=header_pagos)

                pagos_pd = pd.pivot_table(pagos_df, values="monto", index=["tipo_comensal", "dni", "cliente"],
                                          columns=["fecha"], aggfunc=sum, fill_value=0, margins=True)
                pagos_pd.to_excel(writer, sheet_name=mp.name)

                pagos_pd2 = pd.pivot_table(pagos_df, values="monto", index=["tipo_comensal", "dni", "cliente"],
                                           aggfunc=sum, fill_value=0, margins=True)
                pagos_pd2.to_excel(writer, sheet_name="RESUMEN : " + mp.name)

                lines_2_df = pd.DataFrame(lines_2, columns=header)
                lines_2_df.to_excel(writer, sheet_name="COMPILADO : " + mp.name)

                export = True

        if not export:
            raise ValidationError("No existen ventas realizadas")

        writer.save()

        with open("/mnt/extra-addons/"+name,"rb") as file:
            self.ultimo_reporte = base64.b64encode(file.read())
        url="/web/content/%s/%s/%s/%s"%("res.partner",str(self.id),"ultimo_reporte",name)
        return {
            "type":"ir.actions.act_url",
            "url":url,
            "target":"self"
        }

    def cargar_comensales(self):
        if(self.comensales_csv):
            data=base64.b64decode(self.comensales_csv)
            stream = io.StringIO(data.decode("latin-1"))
            #file_csv=csv.reader(file)
            os.system("echo '%s'"%(str(data)))
            with stream as csvfile:
                file_csv = csv.reader(csvfile)
                #print(file_csv)
                #comensales = self.env["res.partner"].search([["es_comensal","=",True],["empresa_id","=",self.id]])
                for comensal in self.comensal_ids:
                    comensal.write({"active":False})
                
                file_csv = list(file_csv)
                cnt=0
                for record in file_csv[1:]:
                    cnt+=1
                    print(cnt,record)
                    if(len(record)<=9):
                        comensal=self.env["res.partner"].sudo().search([["active","=",False],["vat","=",record[1]],["es_comensal","=",True],["empresa_id","=",self.id]])
                        if comensal.exists():
                            comensal = comensal[0]
                            comensal.active=True
                            if not comensal.codigocomensal:
                                comensal.codigocomensal = generador_codigo()
                            comensal.tipo_documento = record[0]
                            comensal.codigo=record[2]
                            comensal.name=record[3]
                            comensal.tipo_comensal = record[4]
                            comensal.area = record[6]
                            comensal.cargo = record[7]
                            comensal.empresa_id = self.id
                        else:
                            self.env["res.partner"].sudo().create({
                                "tipo_documento":record[0],
                                "active":True,
                                "codigocomensal":generador_codigo(),
                                "vat":record[1],
                                "es_empresa":False,
                                "codigo":record[2],
                                "name":record[3],
                                "tipo_comensal":record[4],
                                "area":record[6],
                                "cargo":record[7],
                                "es_comensal":True,
                                "empresa_id":self.id
                            })

        else:
            ValidationError("Para cargar comensales, primero debe cargar la lista de comensales en un formato CSV.")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    es_menu = fields.Boolean("Es Menú")


    def _compute_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }
        return prod_available
"""
class ProductProduct(models.Model):
    _inherit = "product.product"
    es_menu = fields.Boolean("Es Menú")
"""


class Programacion(models.Model):
    _name = "ca.programacion"
    fecha = fields.Date("Fecha")
    product_ids = fields.Many2many("product.product")
    empresa_id = fields.Many2one("res.partner")

class ReportVentas(models.TransientModel):
    _name = "view_report_venta"

    fecha_inicio = fields.Date("Fecha de Inicio")
    fecha_fin = fields.Date("Fecha Fin")
    empresa_id =fields.Many2one("res.partner")

    def button_generar_reporte(self):
        return self.empresa_id.reporte_ventas(self.fecha_inicio,self.fecha_fin)

