from odoo import models,api,fields,_ 
import requests
import json
from odoo.exceptions import UserError
import os

class ResPartner(models.Model):
    _inherit = "res.partner" 
    cliente_api_fe = fields.Boolean(string="Cliente API FE")
    clave_privada = fields.Text(string="Clave Privada")
    clave_publica = fields.Text(string="Clave Pública")
    id_api_cliente  = fields.Char(string="Cliente API ID")
    api_key_fe = fields.Char(string="API FE Key")
    api_secret_fe = fields.Char(string="API FE Secret")
    password = fields.Char(string="Password")
    has_certificate = fields.Boolean(string="Tiene Certificado?")
    cliente_sunat_user = fields.Char(string="Usuario SOL")
    cliente_sunat_password = fields.Char(string="Password SOL")

    ose = fields.Selection(selection=[("sunat","SUNAT"),("efact","EFACT"),("nubefact","NUBEFACT")],default="sunat")
    ose_efact_password = fields.Char("OSE EFACT Password")
    ose_efact_access_key = fields.Char("OSE EFACT Access Key")

    ose_nubefact_user = fields.Char(string="Usuario Nubefact")
    ose_nubefact_password = fields.Char(string="Password Nubefact")

    def generar_credencial_api(self):
        token = self.company_id.get_token()
        url = self.company_id.api_fe_admin_endpoint
        if not self.id_api_cliente:
            raise UserError("El cliente no posee el ID API")
        
        data={
            "method":"Users.generate_new_keys",
            "kwargs":{
                "user_id": self.id_api_cliente
            }
        }
        headers = { 
            "Content-Type": "application/json",
            "Authorization":token
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        data = r.json()
        if "result" in data:
            if "user" in data["result"]:
                if "api_key" in data["result"]["user"]:
                    self.api_key_fe = data["result"]["user"]["api_key"]
                   
                if "api_secret" in data["result"]["user"]:
                    self.api_secret_fe = data["result"]["user"]["api_secret"]
        else:
            message = json.dumps(r.json())
            raise UserError(message)

    def create_user_api_fe(self):
        token = self.company_id.get_token()
        url = self.company_id.api_fe_admin_endpoint
        data={
            "method":"Users.create_user",
            "kwargs":{
                "email": self.email,
                "password": self.password
            }
        }
        headers = { 
            "Content-Type": "application/json",
            "Authorization":token
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        data = r.json()
        os.system("echo '%s'"%(json.dumps(data)))
        if "result" in data:
            if "user" in data["result"]:
                if "id" in data["result"]["user"]:
                    self.id_api_cliente = data["result"]["user"]["id"]

                if "api_key" in data["result"]["user"]:
                    self.api_key_fe = data["result"]["user"]["api_key"]
                   
                if "api_secret" in data["result"]["user"]:
                    self.api_secret_fe = data["result"]["user"]["api_secret"]
            if "error" in data["result"]:
                raise UserError(data["result"]["error"])    
        else:
            message = json.dumps(r.json())
            raise UserError(message)

    def actualizar_credenciales_sunat(self):
        token = self.company_id.get_token()
        url = self.company_id.api_fe_admin_endpoint
        
        if not self.id_api_cliente:
            raise UserError("El cliente no posee el ID API")
        if self.ose == "sunat":
            if not self.cliente_sunat_user:
                raise UserError("El cliente no posee Usuario SOL")
            if not self.cliente_sunat_password:
                raise UserError("El cliente no posee Password SOL")

        elif self.ose == "efact":
            if not self.ose_efact_password:
                raise UserError("El cliente no posee Password de OSE EFACT")
            if not self.ose_efact_access_key:
                raise UserError("El cliente no posee Access Key de OSE EFACT")

        if not self.clave_publica:
            raise UserError("El cliente no posee Clave Pública")
        if not self.clave_privada:
            raise UserError("El cliente no posee Clave Privada")
        if not self.registration_name:
            raise UserError("El cliente no posee Razón Social")
        if not self.vat:
            raise UserError("El cliente no posee RUC")

        data={
            "method":"Users.set_sunat_credentials",
            "kwargs":{
                "user_id": self.id_api_cliente,
                "sunat_user": self.cliente_sunat_user if self.cliente_sunat_user else "-",
                "sunat_password": self.cliente_sunat_password if self.cliente_sunat_password else "-",
                "ose": self.ose,
                "self_signed":self.has_certificate,
                "ose_efact_password": self.ose_efact_password if self.ose_efact_password else "-",
                "ose_efact_access_key": self.ose_efact_access_key if self.ose_efact_access_key else "-",
                'ose_nubefact_user':self.ose_nubefact_user if self.ose_nubefact_user else "-",
                'ose_nubefact_password':self.ose_nubefact_password if self.ose_nubefact_password else "-",
                "private_key": self.clave_privada,
                "public_key": self.clave_publica,
                "razon_social":self.registration_name,
                "ruc":self.vat
            }
        }
        headers = { 
            "Content-Type": "application/json",
            "Authorization":token
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        data = r.json()
        if "result" in data:
            if not data["result"]:
                message = json.dumps(r.json())
                raise UserError(message)
            else:
                return True


class ConsultaComprobantes(models.Model):
    _name = "aafe.consultacomprobante"
    cliente_id = fields.Many2one("res.partner")
    fecha_inicio = fields.Many2one("Fecha de Inicio")
    fecha_finalizacion = fields.Many2one("Fecha de Finalización")
    tipo_comprobante_ids = fields.Many2many("einvoice.catalog.01")
    cliente_rucs = fields.Text("RUC de Clientes")
    series = fields.Text("Series")
    numero_comprobantes = fields.Text("Números de Comprobantes")
    tipo_consulta = fields.Selection(selection=[("simple","Simple"),("avanzado","Avanzado")])

class ResultadoComprobantes(models.TransientModel):
    _name = "aafe.resultadocomprobantes"
    res_comp_linea_ids = fields.One2many("aafe.resultadocomprobantelinea","res_comp_id")

class ResultadoComprobantesLineas(models.TransientModel):
    _name = "aafe.resultadocomprobantelinea"
    _rec_name = "serie"
    serie = fields.Char("Serie")
    numero_comprobante = fields.Char("# Comprobante")
    cliente_receptor_ruc = fields.Char("Cliente receptor")
    tipo_comprobante = fields.Char("Tipo Comprobante")
    res_comp_id = fields.Many2one("aafe.resultadocomprobantes")
    