from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools.profiler import profile

class GuiaRemision(models.Model):
    _inherit = 'efact.guia_remision'

    printer_data = fields.Text(string="Printer Data", required=False, readonly=True, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Guia Remision')])
        data = tpl.render_template(tpl.body_html, 'efact.guia_remision', self.id, post_process=False)
        self.printer_data = data

    """
    @api.multi
    def action_invoice_cancel(self):
        self.printer_data=''
        return super(invoice, self).action_cancel()

    @api.multi
    def action_invoice_open(self):
        res=super(invoice, self).action_invoice_open()
        self.generate_printer_data()
        return res
    """
    def get_tramas(self):
        cant_lineas = 27
        lines = self.guia_remision_line_ids
        c_tramas = len(lines)//cant_lineas +1
        tramas = []
        for trama in range(c_tramas):
            trama_lines = list(lines[trama*cant_lineas:(trama+1)*cant_lineas])
            if len(trama_lines) < cant_lineas:
                x =[False]*(cant_lineas-len(trama_lines))
                trama_lines +=x
            tramas.append(trama_lines)
        return tramas

class invoice(models.Model):
    _inherit = 'account.invoice'

    printer_data = fields.Text(string="Printer Data", required=False, readonly=True, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Invoice')])
        data = tpl.render_template(tpl.body_html, 'account.invoice', self.id, post_process=False)
        self.printer_data = data

    @api.multi
    def action_invoice_cancel(self):
        self.printer_data=''
        return super(invoice, self).action_cancel()

    @api.multi
    def action_invoice_open(self):
        res=super(invoice, self).action_invoice_open()
        self.generate_printer_data()
        return res

    def get_tramas(self):
        lines = self.invoice_line_ids
        cantidad_lineas = 11
        c_tramas = len(lines)//cantidad_lineas +1
        tramas = []
        for trama in range(c_tramas):
            trama_lines = list(lines[trama*cantidad_lineas:(trama+1)*cantidad_lineas])
            if len(trama_lines) < cantidad_lineas:
                x =[False]*(cantidad_lineas-len(trama_lines))
                trama_lines +=x
            tramas.append(trama_lines)
        return tramas

class purchase(models.Model):
    _inherit = 'purchase.order'

    printer_data = fields.Text(string="Printer Data", required=False, readonly=True, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix PO')])
        data = tpl.render_template(tpl.body_html, 'purchase.order', self.id, post_process=False)
        self.printer_data = data


    @api.multi
    def button_confirm(self):
        res = super(purchase, self).button_confirm()
        self.generate_printer_data()
        return res


class picking(models.Model):
    _inherit = 'stock.picking'

    printer_data = fields.Text(string="Printer Data", required=False, readonly=True, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Picking')])
        data = tpl.render_template(tpl.body_html, 'stock.picking', self.id)
        self.printer_data = data


    @api.multi
    def action_confirm(self):
        res = super(picking, self).action_confirm()
        #self.generate_printer_data()
        return res
    """
    @api.multi
    def action_cancel(self):
        res = super(picking, self).action_cancel()
        if self:
            for record in self.filtered(lambda m: m.state in ['confirmed', 'waiting']):
                record.printer_data=''
        return res
    """
class sale(models.Model):
    _inherit = 'sale.order'

    printer_data = fields.Text(string="Printer Data", required=False, readonly=True, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix SO')])
        data = tpl.render_template(tpl.body_html, 'sale.order', self.id)
        self.printer_data = data

    @api.multi
    def action_confirm(self):
        res = super(sale, self).action_confirm()
        self.generate_printer_data()
        return res

    """
    @api.multi
    def action_cancel(self):
        res = super(sale, self).action_cancel()
        self.printer_data=''
        return res
    """
    def get_tramas(self):
        lines = self.order_line
        cantidad_lineas = 16
        c_tramas = len(lines)//cantidad_lineas +1
        tramas = []
        for trama in range(c_tramas):
            trama_lines = list(lines[trama*cantidad_lineas:(trama+1)*cantidad_lineas])
            if len(trama_lines) < cantidad_lineas:
                x =[False]*(cantidad_lineas-len(trama_lines))
                trama_lines +=x
            tramas.append(trama_lines)
        return tramas

  





  