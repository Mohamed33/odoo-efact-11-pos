from odoo import models, fields, api
from datetime import datetime, date, time,timedelta
import os

class ResPartner(models.Model):
    _inherit = 'res.partner'
    es_conductor = fields.Boolean("Es conductor?",default=False)
    es_agencia = fields.Boolean("Es Agencia?",default=False)
    es_destinatario = fields.Boolean("Es Destinatario",default=False)
    brevete = fields.Char("Brevete")

class TipoCarga(models.Model):
    _name = "cm.tipo_carga"
    _description = "Tipo de Carga"
    name = fields.Char("Nombre")
    description = fields.Char("Descripción")
    active = fields.Boolean("Activo",default="True")

class ReporteTransaccion(models.Model):
    _name = "cm.reporte_transaccion"
    _description = "Reporte Transacción"
    

    fecha_servicio = fields.Date(string="Fecha de Servicio",default=fields.Date.today())


    @api.onchange('fecha_servicio')
    def _onchange_fecha_servicio(self):
        if self.fecha_servicio:
            fecha_servicio = datetime.strptime(self.fecha_servicio,"%Y-%m-%d")
            self.mes_servicio = str(fecha_servicio.month).zfill(2)

    mes_servicio = fields.Selection(string="Mes del Servcio",selection=[("01","Enero"),
                                                                        ("02","Febrero"),
                                                                        ("03","Marzo"),
                                                                        ("04","Abril"),
                                                                        ("05","Mayo"),
                                                                        ("06","Junio"),
                                                                        ("07","Julio"),
                                                                        ("08","Agosto"),
                                                                        ("09","Septiembre"),
                                                                        ("10","Octubre"),
                                                                        ("11","Noviembre"),
                                                                        ("12","Diciembre")])
    numero_placa = fields.Char(string="Número de Placa")
    conductor_id = fields.Many2one("res.partner",string="Conductor")
    agencia_id = fields.Many2one("res.partner",string="Agencia")
    destinatario_id = fields.Many2one("res.partner",string="Destinatario")
    cliente_id = fields.Many2one("res.partner",string="Cliente")
    distrito_id = fields.Many2one("res.country.state",string="Distrito")
    tipo_carga = fields.Selection(string="Tipo Carga",selection="_selection_tipo_carga")

    def _selection_tipo_carga(self):
        tipo_cargas = self.env["cm.tipo_carga"].sudo().search([("active","=",True)])
        return [(tipo_carga.id,tipo_carga.name) for tipo_carga in tipo_cargas]

    contenedor = fields.Char(string="Contenedor")
    dua = fields.Char(string="B/L - BK. /  DUA")
    guia_remision = fields.Char(string="Guía de Remisión")

    emitido_desde = fields.Selection(selection=[("sunat","SUNAT"),("see","SEE")],
                                    default="see")

    comprobante_pago = fields.Char(string="Nro. Comprobante")
    account_invoice_id = fields.Many2one("account.invoice","Nro. de Comprobante")

    @api.onchange('emitido_desde')
    def _onchange_emitido_desde(self):
        self.comprobante_pago = ""
        self.account_invoice_id = False    

        self.fecha_vencimiento_factura = ""
        self.fecha_emision_comprobante = ""
        self.cliente_id = False
        self.monto_total = 0
        self.monto_igv = 0
        self.currency_id = False
        self.tipo_cambio = 0
        self.monto_servicio = 0
    
    @api.onchange('account_invoice_id')
    def _onchange_account_invoice_id(self):
        self.fecha_vencimiento_factura = self.account_invoice_id.date_due
        self.fecha_emision_comprobante = self.account_invoice_id.date_invoice
        self.cliente_id = self.account_invoice_id.partner_id.id
        self.monto_total = self.account_invoice_id.amount_total
        self.monto_igv = self.account_invoice_id.amount_tax
        self.currency_id = self.account_invoice_id.currency_id.id
        self.tipo_cambio = self.account_invoice_id.tipo_cambio
        self.monto_servicio = self.account_invoice_id.amount_untaxed
        
    tipo_cambio = fields.Float(string="Tipo de Cambio (PEN->USD)")
    fecha_emision_comprobante = fields.Date(string="Fecha de emisión de Factura")
    periodo_cobro = fields.Integer(string="Periodo Cobro (días)")

    currency_id = fields.Many2one("res.currency",
                                    string="Moneda",
                                    default=lambda self: self.env.user.company_id.currency_id.id)
    monto_servicio = fields.Monetary(string="Monto de Servicio",currency="currency_id")
    monto_adicional = fields.Monetary(string="Monto Adicional",currency="currency_id")
    observacion = fields.Text(string="Observación")
    monto_igv = fields.Monetary(string="Monto IGV",currency="currency_id")
    monto_total = fields.Monetary(string="Monto Total",currency="currency_id")

    currency_soles_id = fields.Many2one("res.currency",
                                    string="Moneda",
                                    default=lambda self: self.env.user.company_id.currency_id.id,
                                    readonly=True)
    monto_servicio_soles = fields.Monetary(string="Monto Servicio en Soles",currency="currency_soles_id")

    
    @api.onchange('tipo_cambio',"monto_total")
    def _onchange_monto_servicio_soles(self):
        if self.currency_soles_id.name == "PEN" and self.currency_id.name == "USD":
            self.monto_servicio_soles = self.monto_total*tipo_cambio
        else:
            self.monto_servicio_soles == 0
    
    dias_trasncurridos = fields.Integer(string="Días Transcurridos")
    #facturas_pagadas = fields.Char(string="Facturas Pagadas")
    #fecha_pago_factura = fields.Date(string="Fecha de Pago de Factura")
    #facturas_vencidas = fields.Char(string="Facturas Vencidas")
    fecha_vencimiento_factura = fields.Date(string="Fecha de Vencimiento de Factura")
    

    @api.onchange("fecha_emision_comprobante")
    def _onchange_fecha_emision_comprobante(self):
        for record in self:
            if record.fecha_emision_comprobante:
                fecha_emision_comprobante = datetime.strptime(record.fecha_emision_comprobante,"%Y-%m-%d")
                os.system("echo '{}'".format(str(fecha_emision_comprobante)))
                periodo_cobro = timedelta(days=record.periodo_cobro)
                fecha_vencimiento_factura = fecha_emision_comprobante + periodo_cobro 
                os.system("echo '{}'".format(type(fecha_emision_comprobante)))
                record.fecha_vencimiento_factura = fecha_vencimiento_factura
                



