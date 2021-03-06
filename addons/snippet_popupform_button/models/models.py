# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
class formulario(http.Controller):

    @http.route('/inscripcion',auth='public',type="json",csrf=False,methods=["POST"])
    def inscripcion(self,name,mobile,email,curso_id,departamento):
        datos_alumno={'name':name,
                      'mobile':mobile,
                      'email':email,
                      'customer':True}
        Alumno=request.env["res.partner"].sudo().create(datos_alumno)
        Curso=request.env["product.template"].sudo().search([["id","=",int(curso_id)]])
        datos_lead = {
            "name":Curso.name+" - "+Alumno.name,
            "partner_id":Alumno.id,
            "planned_revenue":Curso.list_price
        }
        Lead = request.env["crm.lead"].sudo().create(datos_lead)
        if Lead:
            return {"msg":"Estaremos en contacto muy Pronto "}
        else:
            return {"msg":"Error al Registrarse "}
