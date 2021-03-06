# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    zona_id = fields.Many2one("cn.zona", string="Zona")
    ruta_id = fields.Many2one("cn.ruta", string="Ruta")
    tipo_establecimiento_id = fields.Many2one("cn.tipo.establecimiento")

    vitrina = fields.Char("Vitrina")
    compra = fields.Char("Compra")
    linea_credito = fields.Float("Línea de Crédito")

    latitud = fields.Char("Latitud")
    longitud = fields.Char("Longitud")
    segmento = fields.Char("Segmento",default="D")

    objetivo_venta_mensual = fields.Float("Objetivo de venta mensual")
    
    ism_identificador = fields.Char("Identificador ISM",help="Solo para la sucursal ISM")
    
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

    def domain_create(self):
        res = super(ResPartner,self).domain_create()
        res += [("branch_id","=",self.env.user.branch_id.id)]
        return res

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name:
                if record.ruta_id:
                    name = record.name +" - "+ record.ruta_id.name
                else:
                    name = record.name
            else:
                name = "* - *"
            result.append((record.id, name))
        return result

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        payment_term_id = self.env.ref("account.account_payment_term_immediate")
        province_id = self.env.ref("odoope_toponyms.ubigeos_1401").id
        state_id = self.env.ref("odoope_toponyms.ubigeos_14").id
        country_id = self.env.ref("base.pe").id
        res.update({
            "property_payment_term_id":payment_term_id.id,
            "country_id":country_id,
            "province_id":province_id,
            "state_id":state_id,
            "user_id":self.env.uid
        })
        return res
        
    
    @api.constrains('property_payment_term_id')
    def _check_property_payment_term_id(self):
        for record in self:
            if not record.property_payment_term_id and record.type not in ["delivery","other"]:
                raise UserError("El campo plazos de pago es obligatorio")