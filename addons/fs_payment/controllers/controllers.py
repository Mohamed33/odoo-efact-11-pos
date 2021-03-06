# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import culqipy
import datetime

class PagoCulqi(http.Controller):
    
    @http.route('/pago/<token>', auth='public',website=True)
    def pago(self, token, **kw):
        pago=request.env["fs_payment.pagoculqi"].sudo().search([["token","=",token]])
        if pago.exists():
            if pago.state!="Pagado":
                if pago.cuentaculqi_id.public_key:
                    d = {"pago":pago,
                        "public_key":pago.cuentaculqi_id.public_key,
                        "token":token,
                        "email":""}
                    if pago.partner_id:
                        if pago.partner_id.email:
                            d.update({"email":pago.partner_id.email})
                    elif pago.sale_order_id:
                        if pago.sale_order_id.partner_id:
                            if pago.sale_order_id.partner_id.email:
                                d.update({"email":pago.sale_order_id.partner_id.email})
                    return http.request.render('fs_payment.formulario_pago_culqi',d)
                else:
                    return http.request.render('website.404')
            else:
                return http.request.render('fs_payment.pagado_1')
        else:
            return http.request.render('website.404')
    

    @http.route(["/pagar"],type="http",csrf=False, auth='public',methods=["POST"],website=True)
    def pagoculqui(self,**post):
        pago = request.env["fs_payment.pagoculqi"].sudo().search([["token","=",post.get("token_pago")]])
        culqipy.public_key=pago.cuentaculqi_id.public_key
        culqipy.secret_key=pago.cuentaculqi_id.secret_key
                
        if pago.partner_id:
            partner = pago.partner_id
        else:
            partner_obj = request.env["res.partner"].sudo().search(['|',("name","=",post.get("email")),("email","=",post.get("email"))])
            if partner_obj:
                partner = partner_obj[0]
            else:
                partner = request.env["res.partner"].sudo().create({"name":post.get("email"),"email":post.get("email")})
            pago.partner_id = partner.id
            pago.email_from = partner.email

            if pago.sale_order_id:
                if pago.sale_order_id.partner_id.id == request.website.user_id.sudo().partner_id.id:
                    pago.sale_order_id.partner_id = partner.id
                    pago.sale_order_id.partner_invoice_id = partner.id

        if pago.state!="Pagado":
            charge = culqipy.Charge.create({
                            "amount":int(pago.monto*100),
                            "country_code":"PE",
                            "currency_code":pago.moneda,
                            "email":partner.email,
                            "first_name":partner.name,
                            "description":pago.name,
                            "phone_number":partner.mobile if partner.mobile else "-",
                            "source_id":post.get("token_id")
                        })
            if charge["object"]=="charge":
                if charge["outcome"]["type"]=="venta_exitosa":
                    pago.state="Pagado"
                    pago.fecha_pago = datetime.datetime.now()
                    pago.log_response_success=pago.log_response_success if pago.log_response_success else ""+"\n"+str(datetime.datetime.now())+"\n"+json.dumps(charge)
                    pago.sale_order_id.action_confirm()
                    return http.request.render("fs_payment.pago_exitoso",{})
            print(charge)
            if charge["object"]=="error":
                return http.request.render("fs_payment.pago_error",{"msg":charge["merchant_message"]})
    
            pago.log_response_error=pago.log_response_error if pago.log_response_error else "" +"\n"+str(datetime.datetime.now())+"\n"+json.dumps(charge)
        else:
            return http.request.render("fs_payment.pagado",{})
        
        


# class FsPayment(http.Controller):


#     @http.route('/fs_payment/fs_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fs_payment/fs_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fs_payment.listing', {
#             'root': '/fs_payment/fs_payment',
#             'objects': http.request.env['fs_payment.fs_payment'].search([]),
#         })

#     @http.route('/fs_payment/fs_payment/objects/<model("fs_payment.fs_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fs_payment.object', {
#             'object': obj
#         })

