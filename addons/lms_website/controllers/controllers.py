# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import os
from odoo.addons.http_routing.models.ir_http import slug

class LMS(http.Controller):
    @http.route('/lista-cursos-por-categoria',auth='public',website=True)
    def lista_cursos_por_categoria(self):
        categoria_objs = request.env["product.public.category"].sudo().search([])
        categorias = []
        sale_order = request.website.sale_get_order(force_create=True)

        for categoria in categoria_objs:
            curso_objs = request.env["product.product"].sudo().search([("public_categ_ids.id","=",categoria.id),('website_published',"=",True)])
            if len(curso_objs)>0:
                cursos = []
                for curso in curso_objs:
                    order_line = request.env["sale.order.line"].sudo().search([("order_id","=",sale_order.id),("product_id","=",curso.id)])
                    precio_normal = round(curso.list_price,2)
                    precio_ahora = round(sale_order.pricelist_id.get_product_price(product= curso , quantity = 1,partner = sale_order.partner_id),2)
                    descuento = round((precio_normal - precio_ahora)/float(precio_normal),2)*100
                    if order_line:
                        cursos.append([True,curso,{"precio_ahora":precio_ahora,"precio_normal":precio_normal,"descuento":descuento}])
                    else:
                        cursos.append([False,curso,{"precio_ahora":precio_ahora,"precio_normal":precio_normal,"descuento":descuento}])
                categorias.append({"id":str(categoria.id),"name":categoria.name,"cursos":cursos})

        
        
        return request.render('lms_website.lista_cursos_por_categoria',{"categorias":categorias})


    @http.route(['/agregar_producto'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def agregar_producto(self, product_id, add_qty=1, set_qty=1, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
        curso = request.env["product.product"].sudo().browse(int(product_id))
        precio_normal = round(curso.list_price,2)
        precio_ahora = round(sale_order.pricelist_id.get_product_price(product= curso , quantity = 1,partner = sale_order.partner_id),2)
        descuento = round((precio_normal - precio_ahora)/float(precio_normal),2)*100

        sale_order._cart_update(
            product_id = int(product_id),
            add_qty = add_qty,
            set_qty = set_qty
        )
        
        return request.render("lms_website.curso_card",{"curso":[True,curso,{"precio_ahora":precio_ahora,"precio_normal":precio_normal,"descuento":descuento}]})

    @http.route(['/quitar_producto'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def quitar_producto(self, product_id, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        else:
            order_line = request.env["sale.order.line"].sudo().search([("order_id","=",sale_order.id),("product_id","=",int(product_id))])
            order_line.unlink()

            curso = request.env["product.product"].sudo().browse(int(product_id))
            precio_normal = round(curso.list_price,2)
            precio_ahora = round(sale_order.pricelist_id.get_product_price(product= curso , quantity = 1,partner = sale_order.partner_id),2)
            descuento = round((precio_normal - precio_ahora)/float(precio_normal),2)*100

            return request.render("lms_website.curso_card",{"curso":[False,curso,{"precio_ahora":precio_ahora,"precio_normal":precio_normal,"descuento":descuento}]})
    
    @http.route(["/modal_continuar_comprando"],type="http",auth="public",methods=["POST"],website=True,csrf=False)
    def modal_continuar_comprando(self,product_id):
        sale_order = request.website.sale_get_order(force_create=True)
        curso = request.env["product.product"].sudo().browse(int(product_id))
        precio_normal = round(curso.list_price,2)
        precio_ahora = round(sale_order.pricelist_id.get_product_price(product= curso , quantity = 1,partner = sale_order.partner_id),2)
        descuento = round((precio_normal - precio_ahora)/float(precio_normal),2)*100

        return request.render("lms_website.continuar_comprando_modal",{"curso":curso,"precio_ahora":precio_ahora,"precio_normal":precio_normal,"descuento":descuento})


    @http.route(["/comprar_ahora"],type="http",auth="public", csrf=False, website=True)
    def comprar_ahora(self,product_id):
        sale_order = request.website.sale_get_order(force_create=True)
        curso = request.env["product.product"].sudo().browse(int(product_id))
        order_lines = [line for line in sale_order.order_line if line.product_id.id == int(product_id)]
        precio_normal = round(curso.list_price,2)
        precio_ahora = round(sale_order.pricelist_id.get_product_price(product= curso , quantity = 1,partner = sale_order.partner_id),2)
        descuento = round((precio_normal - precio_ahora)/float(precio_normal),2)*100
        
        if descuento <= 0:
            monto = precio_normal
        else :
            monto = precio_ahora

        pago_data = {"sale_order_id":sale_order.id,
                    "name":curso.name,
                    "description":"<b>{}</b>".format(curso.name),
                    "monto":monto,
                    "moneda":curso.currency_id.name}

        if sale_order.partner_id.id != request.website.user_id.sudo().partner_id.id:
            pago_data.update({"partner_id":sale_order.partner_id.id,"email_from":sale_order.partner_id.email if sale_order.partner_id.email else "" })

        pago_culqi = request.env["fs_payment.pagoculqi"].sudo().create(pago_data)
        
        return str(pago_culqi.url)