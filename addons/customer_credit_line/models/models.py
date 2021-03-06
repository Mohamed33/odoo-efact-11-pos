# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from odoo.exceptions import ValidationError

class Customer(models.Model):
    _inherit = "res.partner"
    linea_credito = fields.Float(string="Línea de Crédito")
    total_credito = fields.Float(string="Total Ventas al crédito",compute="compute_monto_por_cobrar")

    def view_form_por_cobrar(self):
        invoice_ids = self.env["account.invoice"].search([["partner_id","=",self.id],["residual",">",0]])
        invoice_ids = [ invoice.id for invoice in invoice_ids]
        return {
            "name":"Cuentas por Cobrar",
            "type":"ir.actions.act_window",
            "view_mode":"tree",
            "res_model":"account.invoice",
            "views":[[request.env.ref("account.invoice_tree").id,"tree"]],
            "domain":[["id","in",invoice_ids]],
            "target":"new"
        }
    
    @api.multi
    def compute_monto_por_cobrar(self):
        for record in self:
            invoice_ids = self.env["account.invoice"].search([["partner_id","=",record.id],["residual",">",0]])
            residuales = [ invoice.residual/invoice.currency_id.rate for invoice in invoice_ids]
            residual_total = sum(residuales)
            record.total_credito = residual_total
    

        
class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def action_invoice_open(self):
        if self.partner_id.linea_credito > self.partner_id.total_credito+self.amount_total or self.partner_id.linea_credito==0:
            res = super(AccountInvoice,self).action_invoice_open()
        else:
            credito_disponible = self.partner_id.linea_credito - self.partner_id.total_credito
            linea_credito_max = self.partner_id.linea_credito

            msg = """No es posible validar la factura debido a que 
                    estaría excediendo el límite del crédito disponible:
                    - Crédito disponible: %f
                    - Línea de crédito: %f """%(credito_disponible,linea_credito_max)

            raise ValidationError(msg)
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    limite_credito_excedido = fields.Boolean("Límite de crédito Excedido",compute="compute_limite_credito_excedido")
    alerta_limite_credito_excedido = fields.Char("Alerta de límite de crédito",compute="compute_limite_credito_excedido")

    @api.depends("partner_id")
    def compute_limite_credito_excedido(self):
        for record in self:
            record.limite_credito_excedido = (record.partner_id.linea_credito < record.partner_id.total_credito+record.amount_total) and record.partner_id.linea_credito!=0
            credito_disponible = record.partner_id.linea_credito - record.partner_id.total_credito
            linea_credito_max = record.partner_id.linea_credito
            record.alerta_limite_credito_excedido = """Esta excediendo el límite del crédito disponible:
                    - Crédito disponible: %9.3f
                    - Línea de crédito: %9.3f """%(credito_disponible,linea_credito_max)
