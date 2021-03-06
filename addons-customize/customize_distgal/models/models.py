# -*- coding: utf-8 -*-

from odoo import api,models,fields
from odoo.exceptions import UserError, ValidationError
import os
from datetime import datetime
import pandas as pd


class ConsolidadoDespachoReport(models.AbstractModel):
    _name = "report.customize_naomis.cn_consolidado_despacho_report"

    @api.model
    def get_report_values(self,docids,data=None):
        account_invoice_ids = self.env["account.invoice"].browse(data["comprobante_ids"])
        lineas_por_producto = {}
        if len(account_invoice_ids)>0:
            fecha_inicio = account_invoice_ids[0].date_invoice
            fecha_fin = account_invoice_ids[-1].date_invoice

        for ai in account_invoice_ids:
            for line in ai.invoice_line_ids:
                if line.product_id in lineas_por_producto:
                    lineas_por_producto[line.product_id].append(line)
                else:
                    lineas_por_producto[line.product_id] = [line]
                
        
        unidad_cantidad_por_producto = []
        for lp in lineas_por_producto:
            unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp] if round(l.price_total)>0]))
            total = sum([l.price_total for l in lineas_por_producto[lp] if round(l.price_total,2)>0])

            #unidad_mayor = round(unidades//round(lp.uom_po_id.factor_inv))
            #unidades = round(unidades%round(lp.uom_po_id.factor_inv))
            
            unidad_menor = round(unidades//round(lp.uom_id.factor_inv))
            unidades = round(unidades%round(lp.uom_id.factor_inv))
            unidad_cantidad_por_producto.append({"unidad":unidades,
                                                "unidad_menor":unidad_menor,
                                                #"unidad_mayor":unidad_mayor,
                                                "total":total,
                                                "product":lp,
                                                "combo":lp.product_tmpl_id.is_combo,"combo_line":False})
            
            bonificacion_unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp] if round(l.price_total,2)==0]))
            
            if bonificacion_unidades>0:
                #bonificacion_unidad_mayor = round(bonificacion_unidades//round(lp.uom_po_id.factor_inv))
                #bonificacion_unidades = round(bonificacion_unidades%round(lp.uom_po_id.factor_inv))
                bonificacion_unidad_menor = round(bonificacion_unidades //round(lp.uom_id.factor_inv))
                bonificacion_unidades = round(bonificacion_unidades%round(lp.uom_id.factor_inv))
                unidad_cantidad_por_producto.append({"unidad":bonificacion_unidades,
                                                        "unidad_menor":bonificacion_unidad_menor,
                                                        #"unidad_mayor":bonificacion_unidad_mayor,
                                                        "total":0,
                                                        "product":lp,
                                                        "combo":lp.product_tmpl_id.is_combo,"combo_line":False})

            if lp.product_tmpl_id.is_combo:
                for lp_c in lp.product_tmpl_id.combo_product_id:
                    unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp] if round(l.price_total)>0]))
                    #unidades_c = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp]]),0)
                    product_c = lp_c.product_id
                    unidades_c = round(unidades*round(lp_c.product_quantity*lp_c.uom_id.factor_inv),0)
                    #unidad_mayor_c = round(unidades_c//round(lp_c.product_id.uom_po_id.factor_inv),0)
                    #unidades_c = round(unidades_c%round(lp_c.product_id.uom_po_id.factor_inv),0)
                    unidad_menor_c = round(unidades_c//round(lp_c.product_id.uom_id.factor_inv,0),0)
                    unidades_c = round(unidades_c%round(lp_c.product_id.uom_id.factor_inv,0),0)
                    unidad_cantidad_por_producto.append({"unidad":unidades_c,
                                                        "unidad_menor":unidad_menor_c,
                                                        #"unidad_mayor":unidad_mayor_c,
                                                        "product":product_c,
                                                        "combo":False,
                                                        "combo_line":True})


        productos_por_categoria = {}
        productos_ordenados = []
        combos = []
        bonificaciones = []

        for x in unidad_cantidad_por_producto:
            if not (x["combo"] or x["combo_line"]):
                if x["total"]>0:
                    productos_ordenados.append([x["product"].supplier_id.name if x["product"].supplier_id else "",
                                                    x["product"].categ_id.parent_id.name if x["product"].categ_id.parent_id else "",
                                                    x["product"].categ_id.name if x["product"].categ_id else "",
                                                    x["product"].name,
                                                    x])
                elif x["total"]==0:
                    bonificaciones.append(x)
                
            else:
                combos.append(x)


        df = pd.DataFrame(productos_ordenados,columns=["proveedor","categoria_padre","categoria","nombre","line"])
        productos_ordenados = df.sort_values(by=["proveedor","categoria_padre","categoria","nombre"]).values.tolist()
        productos_ordenados = [x[4] for x in productos_ordenados]
        productos_por_categoria = sorted(productos_por_categoria.items(),key = lambda x:x[0])
        return {
            'company_name':self.env["res.users"].browse(self.env.uid).company_id.name,
            "data":data,
            "productos_por_categoria":productos_por_categoria,
            "productos_ordenados":productos_ordenados,
            "combos":combos,
            "bonificaciones":bonificaciones,
            "nro_documentos":len(account_invoice_ids),
            "nro_articulos":len(unidad_cantidad_por_producto),
            "monto_total":round(sum([x.amount_total for x in account_invoice_ids]),2),
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_fin,
            "fecha_hoy":fields.Date.today()
        }
    """  
    @api.model
    def get_report_values(self,docids,data=None):
        account_invoice_ids = self.env["account.invoice"].browse(data["comprobante_ids"])
        lineas_por_producto = {}
        if len(account_invoice_ids)>0:
            fecha_inicio = account_invoice_ids[0].date_invoice
            fecha_fin = account_invoice_ids[-1].date_invoice

        for ai in account_invoice_ids:
            for line in ai.invoice_line_ids:
                if line.product_id in lineas_por_producto:
                    lineas_por_producto[line.product_id].append(line)
                else:
                    lineas_por_producto[line.product_id] = [line]
                
        
        unidad_cantidad_por_producto = []
        for lp in lineas_por_producto:
            unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp]]))
            total = sum([l.price_total for l in lineas_por_producto[lp]])
            unidad_mayor = round(unidades//round(lp.uom_po_id.factor_inv))
            unidades = round(unidades%round(lp.uom_po_id.factor_inv))
            unidad_menor = round(unidades //round(lp.uom_id.factor_inv))
            unidades = round(unidades%round(lp.uom_id.factor_inv))
            unidad_cantidad_por_producto.append({"unidad":unidades,
                                                "unidad_menor":unidad_menor,
                                                "unidad_mayor":unidad_mayor,
                                                "total":total,
                                                "product":lp,
                                                "combo":lp.product_tmpl_id.is_combo,"combo_line":False})
            if lp.product_tmpl_id.is_combo:
                for lp_c in lp.product_tmpl_id.combo_product_id:
                    unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp]]),0)
                    product_c = lp_c.product_id
                    unidades_c = round(unidades*round(lp_c.product_quantity*lp_c.uom_id.factor_inv),0)
                    unidad_mayor_c = round(unidades_c//round(lp_c.product_id.uom_po_id.factor_inv),0)
                    unidades_c = round(unidades_c%round(lp_c.product_id.uom_po_id.factor_inv),0)
                    unidad_menor_c = round(unidades_c//round(lp_c.product_id.uom_id.factor_inv,0),0)
                    unidades_c = round(unidades_c%round(lp_c.product_id.uom_id.factor_inv,0),0)
                    unidad_cantidad_por_producto.append({"unidad":unidades_c,
                                                        "unidad_menor":unidad_menor_c,
                                                        "unidad_mayor":unidad_mayor_c,
                                                        "product":product_c,
                                                        "combo":False,
                                                        "combo_line":True})
        productos_por_categoria = {}
        productos_ordenados = []
        combos = []
        bonificaciones = []

        for x in unidad_cantidad_por_producto:
            if not (x["combo"] or x["combo_line"]):
                if x["total"]>0:
                    productos_ordenados.append([x["product"].supplier_id.name if x["product"].supplier_id else "",
                                                    x["product"].categ_id.parent_id.name if x["product"].categ_id.parent_id else "",
                                                    x["product"].categ_id.name if x["product"].categ_id else "",
                                                    x["product"].name,
                                                    x])
                elif x["total"]==0:
                    bonificaciones.append(x)
                
            else:
                combos.append(x)


        df = pd.DataFrame(productos_ordenados,columns=["proveedor","categoria_padre","categoria","nombre","line"])
        productos_ordenados = df.sort_values(by=["proveedor","categoria_padre","categoria","nombre"]).values.tolist()
        productos_ordenados = [x[4] for x in productos_ordenados]
        productos_por_categoria = sorted(productos_por_categoria.items(),key = lambda x:x[0])
        return {
            'company_name':self.env["res.users"].browse(self.env.uid).company_id.name,
            "data":data,
            "productos_por_categoria":productos_por_categoria,
            "productos_ordenados":productos_ordenados,
            "combos":combos,
            "bonificaciones":bonificaciones,
            "nro_documentos":len(account_invoice_ids),
            "nro_articulos":len(unidad_cantidad_por_producto),
            "monto_total":round(sum([x.amount_total for x in account_invoice_ids]),2),
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_fin,
            "fecha_hoy":fields.Date.today()
        }
    """