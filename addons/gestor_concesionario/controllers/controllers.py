# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition

import base64

class GestorConcesionario(http.Controller):

    @http.route('/csv/download/plantilla',auth='public',type="http")
    def download_plantilla_comensal_csv(self):
        header_row='Tipo de Documento, Numero de documento,Codigo - Fotocheck,Apellidos y Nombres,"Tipo Comensal (Obrero,Empleado,etc)",Empresa,Area,Cargo'
        filecontent=base64.b64encode(header_row)
        return request.make_response(header_row,[('Content-Type', 'application/octet-stream'), ('Content-Disposition', content_disposition("Plantilla de comensales.csv"))])


# class GestorConcesionario(http.Controller):
#     @http.route('/gestor_concesionario/gestor_concesionario/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestor_concesionario/gestor_concesionario/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestor_concesionario.listing', {
#             'root': '/gestor_concesionario/gestor_concesionario',
#             'objects': http.request.env['gestor_concesionario.gestor_concesionario'].search([]),
#         })

#     @http.route('/gestor_concesionario/gestor_concesionario/objects/<model("gestor_concesionario.gestor_concesionario"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestor_concesionario.object', {
#             'object': obj
#         })