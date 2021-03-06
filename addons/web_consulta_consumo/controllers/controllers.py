# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import os
from datetime import timedelta,datetime

class web_consulta_consumo(http.Controller):

    @http.route('/consumo', type='http', auth='public')
    def form(self):
        return http.request.render("web_consulta_consumo.template_form", {})

    @http.route('/consultaConsumo', type='http', auth='public', method=["POST"])
    def consulta(self, **post):
        identificador = post.get("identificador")
        os.system("echo '%s' " % (identificador))
        #partner = request.env["res.partner"].sudo().search(['|', ["vat", "=", identificador], ["codigo", "=", identificador], ["es_comensal", "=", True]])
        domain =['|',["partner_id.vat", "=", identificador],['partner_id.codigo','=',identificador],['partner_id.es_comensal','=',True]]
                                                             
        fecha1 = post.get("date1")
        if fecha1:
            domain.append(["date_order",">=", fecha1])
        
        fecha2 = post.get("date2")
        if fecha2:
            domain.append(["date_order", "<=", fecha2])
        
        os.system("echo '%s %s'" % (fecha1, fecha2))
        os.system("echo '%s'" % ("Nuevo"))
        orders = request.env["pos.order"].sudo().search(domain)
        if orders.exists():
            orders.sorted() 
            orders_arr=[]
            monto_total_consumido=0
            for order in orders:
                monto_total_consumido = monto_total_consumido+order.amount_total
                partner = order.partner_id
                orders_arr.append({
                    "name":order.name,
                    "date_order":datetime.strptime(order.date_order,"%Y-%m-%d %H:%M:%S")+timedelta(hours=-5),
                    "amount_total":order.amount_total,
                    "lines":order.lines
                })
		
            return http.request.render("web_consulta_consumo.template_consulta",
                                       {"orders": orders_arr,
                                        "empresa": partner[0].empresa_id.name,
                                        "comensal": partner[0].name,
                                        "monto_total_consumido":monto_total_consumido,
                                        "cantidad_pedidos":len(orders)})
        else:
            return http.request.render("web_consulta_consumo.template_error", {"message": "Usuario No Encontrado"})
