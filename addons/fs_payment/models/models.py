# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from base64 import b64encode
from os import urandom
import hashlib
import random





class Partner(models.Model):
    _inherit = ['res.partner']
    pago_ids = fields.One2many("fs_payment.pagoculqi","partner_id")
    
class CuentaCulqi(models.Model):
    _name = "fs_payment.cuentaculqi"
    name = fields.Char("Nombre")
    tipo = fields.Selection(selection=[("Pruebas","Pruebas"),("Producción","Producción")])
    public_key = fields.Char("Clave Pública")
    secret_key = fields.Char("Clave Privada")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def btn_list_pagos_culqi(self):
        return {
            "type":"ir.actions.act_window",
            "res_model":"fs_payment.pagoculqi",
            "view_mode":"tree,form",
            "domain":[("sale_order_id","=",self.id)],
            "target":"new"

        }

class Settings(models.TransientModel):
    _inherit = "res.config.settings"
    default_cuentaculqi_id = fields.Many2one("fs_payment.cuentaculqi",string="Tipo de Cuenta culqi por Defecto",
                                    default_model="fs_payment.pagoculqi")
    

class PagoCulqi(models.Model):
    _name = "fs_payment.pagoculqi"
    
    _inherit = ['mail.thread']
    
    cuentaculqi_id = fields.Many2one("fs_payment.cuentaculqi","Cuenta de Culqi")

    name= fields.Char("Nombre")
    description = fields.Html(string="Descripción")
    state = fields.Selection(selection=[("Borrador","Borrador"),
                                        ("Enviado","Enviado al correo"),
                                        ("Recibido","Recibido"),
                                        ("Pagado","Pagado")],default="Borrador")
    partner_id = fields.Many2one("res.partner",states={"Borrador":[('readonly',False)]})
    email_from = fields.Char("E-mail",states={"Borrador":[('readonly',False)]})
    mobile  = fields.Char("Celular",states={"Borrador":[('readonly',False)]})
    monto = fields.Float("Monto")

    tiempo_habilitado = fields.Integer("Tiempo Habilitado",default="3")
    fecha_expiracion = fields.Datetime("Fecha de Expiración")
    moneda = fields.Selection(selection=[("PEN","PEN"),("USD","USD")],default="PEN")
    fecha_pago = fields.Datetime("Fecha de pago")
    log_response_success = fields.Text("Log Success")
    log_response_error = fields.Text("Log Error")
    
    url = fields.Char("URL",compute="_compute_url")
    sale_order_id = fields.Many2one("sale.order","Orden de Venta")

    def generate_token(self,length=12):
        chars = list(
            'ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwyz01234567890'
        )
        random.shuffle(chars)
        chars = ''.join(chars)
        sha1 = hashlib.sha1(chars.encode('utf8'))
        token = sha1.hexdigest()
        return token[:length]

    def _default_token(self):
        return self.generate_token(64)

    def enviado(self):
        self.state="Enviado"

    @api.onchange("partner_id") 
    def _cargar_datos_cliente(self):
        self.email_from = self.partner_id.email
        self.mobile = self.partner_id.mobile

    token = fields.Char("Token",states={"Borrador":[('readonly',False)]},default=_default_token)

    @api.depends("token")
    def _compute_url(self):
        url = self.env["ir.config_parameter"].search([("key","=","web.base.url")])
        if url:
            for record in self:
                record.url = url.value+"/pago/"+record.token
    
