# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta
import os
import pytz





class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    porcentaje_descuento = fields.Selection(selection = [("0","Sin Descuento"),
                                                        ("10","Descuento 10%"),
                                                        ("25","Descuento 25%"),
                                                        ("30","Descuento 30%"),
                                                        ("35","Descuento 35%"),
                                                        ("40","Descuento 40%")],default="0")
    
    
    
    @api.onchange("porcentaje_descuento")
    def compute_descuento_lines(self):
        for record in self:
            for line in record.invoice_line_ids:
                line.discount = int(record.porcentaje_descuento)

class Courier(models.Model):
    _name = "gb.courier"        
    name = fields.Char("Nombre")



class SaleOrder(models.Model):
    _inherit = "sale.order"

    porcentaje_descuento = fields.Selection(selection = [("0","Sin Descuento"),
                                                        ("10","Descuento 10%"),
                                                        ("25","Descuento 25%"),
                                                        ("30","Descuento 30%"),
                                                        ("35","Descuento 35%"),
                                                        ("40","Descuento 40%")],default="0")
    
    courier_id = fields.Many2one("gb.courier",string="Courier")
    venta_confirmada = fields.Boolean("Venta Confirmada",default=False)
    fecha_actualizacion_a_venta_confirmada = fields.Datetime("Fecha de Actualización a Venta Confirmada",default=fields.Datetime.now())
    fecha_cancelacion_reserva = fields.Datetime(string="Fecha de Cancelación de Reserva")
    tiempo_restante_cancelacion_reserva = fields.Float(string="Tiempo Restante de Cancelación de Reserva")
    tiempo_reserva = fields.Integer("Tiempo de Reserva (días)",default=0)

    @api.onchange("partner_id")
    def _onchange_courier_id(self):
        for record in self:
            courier_ids = record.partner_id.courier_ids
            if len(courier_ids)>=1:
                record.courier_id = courier_ids[0].id

    @api.multi
    def write(self, values):
        if values.get("state"):
            if self.state != "sale" and values.get("state") == "sale":
                values.update({"fecha_actualizacion_a_venta_confirmada":fields.Datetime.now()})

        result = super(SaleOrder, self).write(values)
    
        return result
    
    def action_cancel(self):
        self.venta_confirmada = False
        return super(SaleOrder,self).action_cancel()


    @api.onchange("porcentaje_descuento")
    def compute_descuento_lines(self):
        for record in self:
            for line in record.order_line:
                line.discount = int(record.porcentaje_descuento)


    @api.multi
    def action_confirm(self):
        msg_error = ""
        for line in self.order_line:
            if line.product_id.virtual_available < line.product_uom_qty:
                msg_error += " * No se puede reservar {cantidad} del producto {producto}, debido a que sólo hay {cantidad_disponible}.".format(cantidad=line.product_uom_qty,producto=line.product_id.name,cantidad_disponible=line.product_id.virtual_available)

        if len(msg_error)>0:
            raise UserError("Alerta!! "+msg_error)
        
        return super(SaleOrder,self).action_confirm()

    def accion_confirmar_venta(self):
        for record in self:
            record.venta_confirmada = True


    @api.model
    def default_get(self, fields):
        os.system("echo 'Nuevo'")
        res = super(SaleOrder, self).default_get(fields)
        res.update({"user_id":self.env.user.id})

        return res
    

    def cron_cancelar_y_convertir_a_borrador(self):
        timezone = pytz.timezone('America/Lima')  
        ventas_no_confirmadas = self.env["sale.order"].sudo().search([["venta_confirmada","=",False],["state","=","sale"]])
        #os.system("echo '%s'"%(ventas_no_confirmadas))
        #ventas_no_confirmadas_1 = [[timezone.localize(datetime.strptime(vnc.fecha_actualizacion_a_venta_confirmada, '%Y-%m-%d %H:%M:%S'))+timedelta(days=1) , timezone.localize(datetime.now())] for vnc in ventas_no_confirmadas]
        #for vnc1 in ventas_no_confirmadas_1:
        #    os.system("echo '%s'"%(vnc1))
        ventas_no_confirmadas = [vnc for vnc in ventas_no_confirmadas 
                                        if timezone.localize(datetime.strptime(vnc.fecha_actualizacion_a_venta_confirmada, '%Y-%m-%d %H:%M:%S'))+timedelta(days=vnc.tiempo_reserva) < timezone.localize(datetime.now()) and vnc.tiempo_reserva > 0]
        
        for vnc in ventas_no_confirmadas:
            vnc.action_cancel()
            vnc.action_draft()



class ResPartner(models.Model):
    _inherit = "res.partner"

    user_id = fields.Many2one("res.users",default="_default_set_user")
    courier_ids = fields.Many2many("gb.courier")

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res.update({"user_id":self.env.user.id})
    
        return res


class Settings(models.TransientModel):
    _inherit = "res.config.settings"

    default_tiempo_reserva = fields.Integer(string="Tiempo de Reserva",default_model="sale.order")
    
