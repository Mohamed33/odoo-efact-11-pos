# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta,datetime
from odoo.exceptions import UserError, ValidationError

# class hlt_sales_profit(models.Model):
#     _name = 'hlt_sales_profit.hlt_sales_profit'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class SaleOrder(models.Model):
    
    _inherit = ['sale.order']

    cantidad_letras = fields.Integer("Cantidad Letras")
    tasa = fields.Float("Tasa (%)")
    comision_letra = fields.Float("Comisión por letra")
    total_comision = fields.Float("Total de Comisión",compute ="_compute_rentabilidad")
    total_interes = fields.Float("Total de Interés",compute ="_compute_rentabilidad")
    total_financiamiento = fields.Float("Total de Financiamiento",compute ="_compute_rentabilidad")
    importe_letra = fields.Float("Importe Letra")
    fecha_inicio = fields.Date("Fecha de Inicio")
    rentabilidad_neta = fields.Float("Rentabilidad Neta (%)",compute ="_compute_rentabilidad_final")
    
    costo_financiamiento = fields.Float("Costo de Financiamiento (%)")
    costo_comision_vendedor = fields.Float("Costo de Comisión de Vendedor (%)")
    costo_administrativo = fields.Float("Costo Administrativo (%)")
    
    periodo = fields.Selection(selection=[("15","Quincenal"),("30","Mensual"),("45","45 días")],default="30")

    detalle_letra_ids = fields.One2many("detalle.letras","sale_order_id",string="Detalle de Letras")

    margen = fields.Float("Márgen (%)",compute="_compute_margen")
    forma_pago = fields.Selection(string="Forma de Pago",
                                    selection=[("financiado","Financiado"),("al_contado","Al Contado")],
                                    default="financiado",
                                    required=True)


    @api.depends("order_line")
    def _compute_margen(self):
        for record in self:
            costo=0
            for line in record.order_line:
                costo+=line.purchase_price*line.product_uom_qty
            if costo!=0:
                record.margen=100*record.margin/costo
            else:
                record.margen=0

    def compute_detalle_letras(self):
        detalle_letras = []
        cantidad_dias = 0
        total_comision = 0
        total_interes = 0
        if len(self.detalle_letra_ids): 
            for letra in self.detalle_letra_ids:
                letra.unlink()
        for i in range(self.cantidad_letras):
            cantidad_dias=cantidad_dias+int(self.periodo)
            importe_letra = self.amount_total/self.cantidad_letras if self.cantidad_letras!=0 else 0
            interes = importe_letra*(1-(1/((1+self.tasa/100)**(cantidad_dias/360))))
            detalle_letras.append({
                "fecha_venc":datetime.strptime(self.fecha_inicio,"%Y-%m-%d")+timedelta(days=cantidad_dias),
                "cantidad_dias":cantidad_dias,
                "importe_letra":importe_letra,
                "tasa":self.tasa,
                "comision":self.comision_letra
            })
            total_comision = total_comision+self.comision_letra
            total_interes = total_interes+interes
        
        self.total_comision=total_comision
        self.total_interes=total_interes
        self.costo_financiamiento = 100*(total_comision+total_interes)/self.amount_total
        self.detalle_letra_ids = detalle_letras
        
    @api.depends("detalle_letra_ids")
    def _compute_rentabilidad(self):
        for record in self:
            total_comision = 0
            total_interes = 0
            for line in record.detalle_letra_ids:
                total_comision += line.comision
                total_interes += line.interes

            record.total_comision = total_comision
            record.total_interes = total_interes
            record.total_financiamiento = total_comision+ total_interes
            if record.amount_total!=0:
                record.costo_financiamiento = 100*record.total_financiamiento/record.amount_total
            else:
                record.costo_financiamiento =0
    
    @api.depends("margen","costo_financiamiento","costo_comision_vendedor","costo_administrativo")
    def _compute_rentabilidad_final(self):
        for record in self:
            if record.forma_pago == "financiado":
                record.rentabilidad_neta = record.margen-record.costo_financiamiento-record.costo_comision_vendedor-record.costo_administrativo
            elif record.forma_pago == "al_contado":
                record.rentabilidad_neta = record.margen-record.costo_comision_vendedor-record.costo_administrativo

class DetalleLetras(models.Model):
    _name = "detalle.letras"
    fecha_venc = fields.Date("Fecha de Vencimiento",compute="_compute_interes")
    cantidad_dias = fields.Integer("Cantidad de Días")
    importe_letra = fields.Float("Importe de Letra")
    comision = fields.Float("Comisión") 
    interes = fields.Float("Interés",compute="_compute_interes") 
    tasa = fields.Float("Tasa")
    sale_order_id = fields.Many2one("sale.order")


    @api.depends("cantidad_dias","importe_letra","interes")
    def _compute_interes(self):
        for record in self:
            record.interes = record.importe_letra*(1-(1/((1+record.tasa/100)**(record.cantidad_dias/360))))
            if record.sale_order_id.fecha_inicio:
                record.fecha_venc = datetime.strptime(record.sale_order_id.fecha_inicio,"%Y-%m-%d")+timedelta(days=record.cantidad_dias if record.cantidad_dias else 0)
            else:
                raise ValidationError("Debe configurar una fecha de inicio")