from odoo import fields,api,models 
from odoo.exceptions import UserError, ValidationError

import re

patron_dni = re.compile("\d{8}$")
patron_ruc = re.compile("[12]\d{10}$")

class ResPartner(models.Model):
    _inherit = "res.partner"    
    
    
    @api.onchange('tipo_documento')
    def _onchange_tipo_documento(self):
        for record in self:
            if record.tipo_documento == '6':
                record.company_type = "company"
            else:
                record.company_type = "person"
    
    
    @api.onchange('company_type')
    def _onchange_company_type(self):
        for record in self:
            if record.company_type == "company":
                self.tipo_documento = '6'
            else:
                self.tipo_documento = '0'
                if not self.vat:
                    self.vat = '0'

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                self.name = self.name.strip()
                self.name = self.name.replace("\n"," - ")
    
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name and record.type not in ["delivery","other"]:
                if (len(record.name)<4 or  len(record.name) >250) :
                    raise UserError("La cantidad de carácteres del cliente debe ser mayor a 4 y menor a 250.") 
            
    
    def domain_create(self):
        return [("company_id","=",self.env.user.company_id.id)]
    
    @api.model
    def create(self, vals):
        vat = vals.get("vat",False)
        vat = vat.strip() if vat else ""
        tipo_documento = vals.get("tipo_documento",False)
        name = vals.get("name","")
        name = name.strip() if name else ""
        domain = [("tipo_documento","=","0"),
                    ("name","=",name)] + self.domain_create()
        cliente_varios = self.env["res.partner"].search(domain)
        if cliente_varios.exists():
            msg = "El cliente ya existe con el nombre {}.".format(cliente_varios[0].name)
            raise UserError(msg)
        
        if not vat and tipo_documento in ["1","6"]:
            msg = "El número de documento de identidad del cliente es obligatorio"
            raise UserError(msg)

        #RUC y DNI son únicos
        if vat and tipo_documento in ["1","6"]:
            domain = [("vat","=",vat),
                        ("tipo_documento","=",tipo_documento)]+self.domain_create()

            cliente = self.env["res.partner"].search(domain)
            if tipo_documento == "1":
                if not patron_dni.match(vat):
                    msg = "El número de DNI tiene un formato incorrecto"
                    raise UserError(msg)

            if tipo_documento == "6":
                if not patron_ruc.match(vat):
                    msg = "El número de RUC tiene un formato incorrecto"
                    raise UserError(msg)

            if cliente.exists():
                msg = "El Número de Identidad del cliente ingresado ya existe y se encuentra con el nombre {}.".format(cliente[0].name)
                raise UserError(msg)
                
        if  tipo_documento =="6":
            vals.update({"company_type":"company"})
        else:
            vals.update({"company_type":"person"})
        
        if not vals.get("registration_name",False):
            vals.update({"registration_name":vals.get("name")})
        
        if not vals.get("zip",False):
            vals.update({"zip":"-"})

        return super(ResPartner, self).create(vals)