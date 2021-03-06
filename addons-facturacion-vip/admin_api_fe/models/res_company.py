from odoo import models,api,fields,_   
import requests
import json
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"
    api_fe_admin_endpoint = fields.Char(string="Endpoint")
    api_fe_admin_login = fields.Char(string="Login API FE")
    api_fe_admin_password = fields.Char(string="Password API FE")

    def get_token(self):
        url = self.api_fe_admin_endpoint
        data={
            "method":"Login.login",
            "args":[self.api_fe_admin_login,self.api_fe_admin_password]
        }
        headers = { 
            "Content-Type": "application/json",
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        data = r.json()
        if "result" in data:
            if "token" in data["result"]:
                return data["result"]["token"]
        
        raise UserError(json.dumps(r.json()))
        

    def sync_clientes(self):
        token = self.get_token()
        url = self.api_fe_admin_endpoint
        data={
            "method":"Users.list_users"
        }
        headers = { 
            "Content-Type": "application/json",
            "Authorization":token
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        data = r.json()
        if "result" in data:
            clientes = data["result"]
            for cliente in clientes:
                cliente_obj = self.env["res.partner"].search([["id_api_cliente","=",cliente["id"]]])
                if not cliente_obj.exists():
                    cliente_data={
                        "name":cliente["razon_social"] if cliente["razon_social"] else "-",
                        "registration_name":cliente["razon_social"] if cliente["razon_social"] else "-",
                        "email":cliente["email"],
                        "password":cliente["password"],
                        "vat":cliente["ruc"],
                        "api_key_fe":cliente["api_key"],
                        "clave_privada":cliente["private_key"],
                        "clave_publica":cliente["public_key"],
                        "cliente_api_fe":True,
                        "cliente_sunat_user":cliente["sunat_user"],
                        "cliente_sunat_password":cliente["sunat_password"],
                        "id_api_cliente":cliente["id"]
                    }
                    self.env["res.partner"].create(cliente_data)
                else:
                    cliente_data={
                        "name":cliente["razon_social"],
                        "registration_name":cliente["razon_social"],
                        "email":cliente["email"],
                        "password":cliente["password"],
                        "vat":cliente["ruc"],
                        "api_key_fe":cliente["api_key"],
                        "clave_privada":cliente["private_key"],
                        "clave_publica":cliente["public_key"],
                        "cliente_api_fe":True,
                        "cliente_sunat_user":cliente["sunat_user"],
                        "cliente_sunat_password":cliente["sunat_password"],
                        "id_api_cliente":cliente["id"]
                    }
                    cliente_obj.write(cliente_data)
        else:
            message = json.dumps(data)
            raise UserError(message)

        
        
        



