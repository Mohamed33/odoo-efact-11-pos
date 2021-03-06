# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.profiler import profile
import os


class ResBranch(models.Model):
    _name = "res.branch"
    name = fields.Char("Nombre")
    company_id = fields.Many2one("res.company",default = lambda self: self.env.user.company_id.id,string="Compañia")
    supplier_ids = fields.Many2many("res.partner",string="Proveedor")
    user_id = fields.Many2one("res.users","Usuario")

class ResUser(models.Model):
    _inherit = "res.users"
    branch_id = fields.Many2one("res.branch",string="Sucursales Permitidas")
    supplier_ids = fields.Many2many("res.partner",related="branch_id.supplier_ids")
    # supplier_id = fields.Many2one("res.partner",string="Sucursal")

class ResCompany(models.Model):
    _inherit = "res.company"
    branch_ids = fields.One2many("res.branch","company_id")

class Zona(models.Model):
    _name = "cn.zona"
    code = fields.Char("Código")
    name = fields.Char("Nombre")
    company_id = fields.Many2one("res.company",default = lambda self: self.env.user.company_id.id)
    active = fields.Boolean("Activo",default=True)
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

class Ruta(models.Model):
    _name = "cn.ruta"
    code = fields.Char("Código")
    name = fields.Char("Nombre")
    zona_id = fields.Many2one("cn.zona")
    company_id = fields.Many2one("res.company",default = lambda self: self.env.user.company_id.id)
    active = fields.Boolean("Activo",default=True)
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

class TipoEstablecimiento(models.Model):
    _name = "cn.tipo.establecimiento"
    code = fields.Char("Código")
    name = fields.Char("Nombre")
    company_id = fields.Many2one("res.company",default = lambda self: self.env.user.company_id.id)
    active = fields.Boolean("Activo",default=True)
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

class ProgramacionRuta(models.Model):
    _name = "cn.programacion.ruta"

    ruta_id = fields.Many2one("cn.ruta","Ruta")
    zona_id = fields.Many2one("cn.zona",related="ruta_id.zona_id",readonly=True,string="Zona")

    dia_visita = fields.Selection(selection=[("DOMINGO","DOMINGO"),
                                            ("LUNES","LUNES"),
                                            ("MARTES","MARTES"),
                                            ("MIERCOLES","MIERCOLES"),
                                            ("JUEVES","JUEVES"),
                                            ("VIERNES","VIERNES"),
                                            ("SABADO","SABADO")],string="Día de visita")

    user_id = fields.Many2one("res.users","Vendedor")
    company_id = fields.Many2one("res.company",default = lambda self: self.env.user.company_id.id)
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)


class AccountInvoiceGuiaRemisionMasivo(models.Model):
    _inherit = "account.invoice"
    ruta_id = fields.Many2one("cn.ruta",related="partner_id.ruta_id")
    
    
    @api.multi
    def multiples_guia_remision(self):
        #print([r.move_name for r in self])
        #print("multiple_guia_remision")
        try:
            guia_remision = self.env["efact.guia_remision"].create({
                "documento_asociado":"comprobante_pago",
                "comprobante_pago_ids":[(6,0,[r.id for r in self])]
            })
            guia_remision._onchange_comprobante_pago()
            return {
                "type":"ir.actions.act_window",
                "res_model":"efact.guia_remision",
                "res_id":guia_remision.id,
                "view_mode":"form,tree",
                "target":"self"
            }
        except:
            raise UserError("No se ha podido crear la guía de Remisión")

    def action_view_consolidar_comprobantes_gr(self):
        return {
            "type":"ir.actions.act_window",
            "name":"Guía de Remisión Masiva",
            "res_model":"view.guia.remision.consolidado",
            "view_mode":"tree,form",
            "context":{
                "default_fecha_inicio": fields.Date.today(),
                "default_fecha_limite":fields.Date.today()
            }
        }


class AccountInvoiceViewGuiaRemisionConsolidadoRel(models.Model):
    _name = "account.invoice.view.guia.remision.consolidado.rel"
    view_guia_remision_consolidado_id = fields.Many2one("view.guia.remision.consolidado")
    account_invoice_id = fields.Many2one("account.invoice")
    state = fields.Boolean("Estado")

class ViewGuiaRemisionConsolidado(models.Model):
    _name = 'view.guia.remision.consolidado'
    _description = 'Consolidar Guía de Remisión'
    
    fecha_inicio = fields.Date("Fecha Inicio")
    fecha_limite  = fields.Date("Fecha Límite")
    ruta_ids = fields.Many2many("cn.ruta")
    transportista_id = fields.Many2one("res.users",string="Transportista")
    vehicle_id = fields.Many2one("efact.vehicle",string="Vehículo")

    seleccion_vendedor = fields.Selection(selection=[("todos_vendedores","Todos los Vendedores"),
                                                    ("seleccionar_vendedor","Algunos Vendedores")],
                                            string="Selección de Vendedores",
                                            default="todos_vendedores")

    
    
    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for record in self:
            if record.fecha_inicio and record.fecha_limite:
                if record.fecha_inicio != record.fecha_limite:
                    name = "Comprobantes desde {} al {}".format(record.fecha_inicio,record.fecha_limite)
                else:
                    name = "Comprobantes del {}".format(record.fecha_limite)
            else:
                name = "Nuevo"
            result.append((record.id, name))
        return result
    
    
    @api.onchange("seleccion_vendedor")
    def _onchange_selecciona_vendedor(self):
        vendedor_ids = [(6,0,[])]

    vendedor_ids = fields.Many2many("res.users")

    comprobante_ids = fields.Many2many("account.invoice")
    
    sale_order_ids = fields.Many2many("sale.order")
    
    printer_data = fields.Text(string="Printer Data", required=False, readonly=True)

    comprobante_secuencia_ids = fields.Many2many("invoice.secuencia")

    def cargar_comprobantes(self):
        for record in self:
            domain = [["date_invoice",">=",record.fecha_inicio],
                        ["date_invoice","<=",record.fecha_limite],
                        ['journal_id.invoice_type_code_id','in',['00','01','03']],
                        ['state','in',['open','paid']]]
            if len(record.ruta_ids):
                domain.append(["ruta_id","in",[r.id for r in record.ruta_ids]])
            if len(record.vendedor_ids):
                domain.append(["user_id","in",[v.id for v in record.vendedor_ids]])
            
            comps = self.env["account.invoice"].search(domain)
            comps = comps.sorted(key =  lambda r:r.number)
            comprobante_ids = [c.id for c in comps]
            comprobante_secuencia_ids = [(0,0,{"invoice_id":comp.id,"secuencia":idx+1}) for idx,comp in enumerate(comps) if comp.journal_id.invoice_type_code_id in ["01","03"]]
            record.comprobante_ids = [(6,0,comprobante_ids)]
            record.comprobante_secuencia_ids = [(6,0,[])]
            record.comprobante_secuencia_ids = comprobante_secuencia_ids
            record.generate_printer_data()
    
    def generar_guia_remision(self):
        try:
            print([r.id for r in self.comprobante_ids])
            
            guia_remision = self.env["efact.guia_remision"].create({
                "documento_asociado":"comprobante_pago",
                "comprobante_pago_ids":[(6,0,[r.id for r in self.comprobante_ids])]
            })
            guia_remision._onchange_comprobante_pago()
            return {
                "type":"ir.actions.act_window",
                "res_model":"efact.guia_remision",
                "res_id":guia_remision.id,
                "view_mode":"form,tree",
                "target":"self"
            }
        except:
            raise UserError("No se ha podido crear la guía de Remisión")    
    
    def imprimir_liquidacion_despacho(self):
        comprobantes = self.comprobante_ids
        if len(self.comprobante_ids)>0:
            report_obj = self.env.ref("customize_naomis.cn_report_liquidacion_despacho")
            return report_obj.report_action(comprobantes)
        else:
            raise ValidationError("No se han encontrado comprobantes para el reporte de Liquidación de desapacho.")
    
    def imprimir_consolidado_despacho(self):
        comprobantes = self.comprobante_ids
        if len(self.comprobante_ids)>0:
            report_obj = self.env.ref("customize_naomis.cn_report_consolidado_despacho")
            data = {
                "seleccion_vendedor":self.seleccion_vendedor,
                "vendedores":";".join([v.name for v in self.vendedor_ids]),
                "transportista": self.transportista_id.name if self.transportista_id else "-",
                "comprobante_ids":[comp.id for comp in comprobantes]
            }
            return report_obj.report_action(comprobantes,data)
        else:
            raise ValidationError("No se han encontrado comprobantes para el reporte de Consolidado de desapacho.")
    
    def generate_printer_data(self):
        printer_data = ""
        for record in self:
            for comp in sorted(record.comprobante_ids,key = lambda x:x.number):
                if comp.journal_id.invoice_type_code_id in ["01","03"]:
                    comp.generate_printer_data()
                    printer_data = printer_data + comp.printer_data
            record.printer_data = printer_data
    
    def wizard_impresion_parcial(self):
        return {
            "type":"ir.actions.act_window",
            "name":"Impresión Parcial",
            "res_model":"wizard.print.invoice.dot.matrix",
            "view_mode":"form",
            "target":"self",
            "context":{
                "default_guia_remision_consolidado_id":self.id
            }

        }
