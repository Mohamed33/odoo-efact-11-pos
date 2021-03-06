# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.http import request

class LetraDeCambio(models.Model):
    _name = "lc.letra_de_cambio"
    _inherit = ['mail.thread',"account.abstract.payment"]
    _description = "Letras de Cambio"
    _order = "fecha_vencimiento desc"

    invoice_ids = fields.Many2many("account.invoice",string="Facturas",track_visibility='onchange')
    fecha_emision = fields.Date(string="Fecha de Emisión",required=True,track_visibility='onchange')
    fecha_vencimiento = fields.Date(string="Fecha de Vencimiento",required=True,track_visibility='onchange')
    numero = fields.Char(string="Número de Letra",required=True,track_visibility='onchange')
    name = fields.Char(string="Nombre",required =True,compute="name_get")

    """
    def create(self,vals):
        rec = super(LetraDeCambio,self).create(vals)
        return rec
    """

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            fecha_emision = record.fecha_emision if record.fecha_emision else ""
            numero = record.numero if record.numero else " sin número"
            invoices = ",".join([inv.move_name for inv in record.invoice_ids])
            name = fecha_emision+" - "+numero + " - " + invoices
            result.append((record.id, name))
        return result

    def validate(self):
        pass
"""
class RegistrarLetrasDeCambio(models.Model):
    _name= "lc.form"
    letra_de_cambio_ids = fields.One2many("lc.lentra_de_cambio","registro_letra_id",string="Letras de Cambio")

"""

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    letra_de_cambio_ids = fields.Many2many("lc.letra_de_cambio",string="Letras de Cambio")

    def action_view_form_crear_letras(self):
        if self.type == 'out_invoice':
            partner_type = 'customer' 
            payment_type = 'inbound'
        elif self.type == 'in_invoice':
            partner_type =  'supplier'
            payment_type = 'outbound'

        return {
            "name":"Crear Letras de Cambio",
            "type":"ir.actions.act_window",
            "view_mode":"form",
            "res_model":"lc.letra_de_cambio",
            "views":[[request.env.ref("letra_de_cambio.view_form_crear_letras_de_cambio").id,"form"]],
            "target":"new",
            "context":{
                "default_amount":self.residual,
                "default_partner_id":self.partner_id.id,
                "default_partner_type":partner_type,
                "default_payment_type":payment_type,
                "default_invoice_ids":[(6,0,[self.id])]
                #"default_payment_method_id":
            }
        }

    def action_view_tree_letras_de_cambio(self):
        if self.type == 'out_invoice':
            vista_tree = "letra_de_cambio.view_tree_letras_de_cambio"
            vista_form = "letra_de_cambio.view_form_letras_de_cambio"
            partner_type = 'customer' 
            payment_type = 'inbound'
        elif self.type == 'in_invoice':
            vista_tree = "letra_de_cambio.view_tree_letras_de_cambio_compra"
            vista_form = "letra_de_cambio.view_form_letras_de_cambio_compra"
            partner_type =  'supplier'
            payment_type = 'outbound'
        
        return {
            "name":"Letras de Cambio",
            "type":"ir.actions.act_window",
            "view_mode":"tree,form",
            "res_model":"lc.letra_de_cambio",
            "views":[[request.env.ref(vista_tree).id,"tree"],[request.env.ref(vista_form).id,"form"]],
            "target":"self",
            "domain":[("id","in",[lc.id for lc in self.letra_de_cambio_ids])],
            "context":{
                "default_amount":self.residual,
                "default_partner_id":self.partner_id.id,
                "default_partner_type":partner_type,
                "default_payment_type":payment_type,
                "default_invoice_ids":[(6,0,[self.id])]
            }
        }


# class letra_de_cambio(models.Model):
#     _name = 'letra_de_cambio.letra_de_cambio'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100