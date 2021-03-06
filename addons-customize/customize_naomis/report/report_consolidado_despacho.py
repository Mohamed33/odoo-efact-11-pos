from odoo import api,models,fields
from odoo.exceptions import UserError, ValidationError
import os
from datetime import datetime



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
            unidades = round(sum([l.quantity*l.uom_id.factor_inv for l in lineas_por_producto[lp]]))
            total = sum([l.price_subtotal for l in lineas_por_producto[lp]])
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
                                                        "combo":False,"combo_line":True})
        productos_por_categoria = {}
        combos = []
        for x in unidad_cantidad_por_producto:
            if not (x["combo"] or x["combo_line"]):
                if x["product"].categ_id:
                    if x["product"].categ_id.name in productos_por_categoria:
                        productos_por_categoria[x["product"].categ_id.name].append(x)
                    else:
                        productos_por_categoria[x["product"].categ_id.name] = [x]
                else:
                    if "Sin Categoria" in productos_por_categoria:
                        productos_por_categoria["Sin Categoria"].append(x)
                    else:
                        productos_por_categoria["Sin Categoria"] = [x]
            else:
                combos.append(x)
        productos_por_categoria = sorted(productos_por_categoria.items(),key = lambda x:x[0])
        return {
            'company_name':self.env["res.users"].browse(self.env.uid).company_id.name,
            "data":data,
            "productos_por_categoria":productos_por_categoria,
            "combos":combos,
            "nro_documentos":len(account_invoice_ids),
            "nro_articulos":len(unidad_cantidad_por_producto),
            "monto_total":round(sum([x.amount_total for x in account_invoice_ids]),2),
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_fin,
            "fecha_hoy":fields.Date.today()
        }