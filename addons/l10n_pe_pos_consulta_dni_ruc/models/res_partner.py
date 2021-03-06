# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError, ValidationError
import requests


class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model
    def consulta_datos(self, tipo_documento, nro_documento, format='json'):
        if nro_documento:
            cliente = self.env["res.partner"].sudo().search([("vat","=",nro_documento)])
            if cliente.exists():
                msg = "El Número de Identidad del cliente ingresado ya existe, y pertenece al usuario {}".format(cliente[0].name)
                raise ValidationError(msg)
                
        if tipo_documento=="dni":
            d = self.get_person_name_v3(nro_documento)
            if d:
                return {"data":{"nombres":d}}
            else:
                return {"error":True,"message":"No se ha encontrado el DNI"}
            
        elif tipo_documento=="ruc":
            d = self.consulta_ruc_api(nro_documento)
            if d:
                return {"data":d}
            else:
                return {"error":True,"message":"No se ha encontrado el RUC"}
