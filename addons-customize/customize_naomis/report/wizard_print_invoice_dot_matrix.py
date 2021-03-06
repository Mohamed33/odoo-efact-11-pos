from odoo import fields,models,api 
from odoo.exceptions import UserError, ValidationError

class InvoiceSecuencia(models.Model):
    _name = "invoice.secuencia"
    invoice_id = fields.Many2one("account.invoice")
    secuencia = fields.Integer("Orden")
    numero = fields.Char(related="invoice_id.number")
    partner_id = fields.Many2one("res.partner",related="invoice_id.partner_id")
    user_id = fields.Many2one("res.users",related="invoice_id.user_id")



class WizardPrintInvoiceDotMatrix(models.TransientModel):
    _name = "wizard.print.invoice.dot.matrix"
    
    
    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for record in self:
            if record.secuencia_fin and record.secuencia_inicio:
                name = "Secuencia de Impresión {} - {}".format(record.secuencia_inicio,record.secuencia_fin)
                result.append((record.id, name))
            else:
                name = "Nuevo"
        return result
    
    
    secuencia_inicio= fields.Integer("Inicio")
    secuencia_fin= fields.Integer("Fin")
    guia_remision_consolidado_id = fields.Many2one("view.guia.remision.consolidado")
    invoice_secuencia_ids = fields.Many2many("invoice.secuencia")
    printer_data = fields.Text(string="Printer Data", required=False, readonly=True)

    
    def cargar_comprobantes(self):
        comps = [comp.id
                    for comp in self.guia_remision_consolidado_id.comprobante_secuencia_ids 
                        if comp.secuencia>=self.secuencia_inicio and comp.secuencia<=self.secuencia_fin]
        self.invoice_secuencia_ids = []
        self.invoice_secuencia_ids = [(6,0,comps)]
        self.generate_printer_data()
            

    def generate_printer_data(self):
        printer_data = ""
        for record in self:
            for comp in record.invoice_secuencia_ids.sorted(key=lambda comp:comp.secuencia):
                comp.invoice_id.generate_printer_data()
                printer_data = printer_data + comp.invoice_id.printer_data
            record.printer_data = printer_data

    @api.constrains('secuencia_inicio')
    def inicio_check(self):
        for record in self:
            if record.secuencia_inicio >= record.secuencia_fin:
                raise UserError("El número de inicio debe ser menor al de Fin")
    
    @api.constrains('secuencia_fin')
    def fin_check(self):
        for record in self:
            if record.secuencia_inicio >= record.secuencia_fin:
                raise UserError("El número de fin debe ser Mayor al de inicio")
    
    
    @api.model
    def default_get(self, fields):
        res = super(WizardPrintInvoiceDotMatrix, self).default_get(fields)
        guia_remision_consolidado_id = res.get("guia_remision_consolidado_id",False)
        if guia_remision_consolidado_id:
            guia_remision_consolidado_obj = self.env["view.guia.remision.consolidado"].browse(guia_remision_consolidado_id)
            res["secuencia_inicio"] = 1
            res["secuencia_fin"] = len(guia_remision_consolidado_obj.comprobante_secuencia_ids)
        return res
        
    