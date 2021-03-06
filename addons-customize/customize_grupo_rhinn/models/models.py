# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit = ['product.template']
    price_min = fields.Float("Precio Mínimo")


class ProductProduct(models.Model):
    _inherit = ['product.product']
    price_min = fields.Float("Precio Mínimo")

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    numero_guia = fields.Char("Número de Guía",related="invoice_picking_id.numero_guia")
    location_id = fields.Many2one("stock.location")

    @api.multi
    @api.onchange("picking_transfer_id")
    def _onchange_location_id(self):
        for record in self:
            record.location_id = record.picking_transfer_id.default_location_src_id.id
            for line in record.invoice_line_ids:
                line.location_id = record.picking_transfer_id.default_location_src_id.id
                if line.lot_id:
                    line.lot_id = False
                
    @api.constrains("invoice_line_ids")
    def restricion_lineas(self):
        for record in self:
            if record.type != "in_invoice":
                for  r in record.invoice_line_ids:
                    if (r.price_unit-r.descuento_unitario)<r.product_id.price_min:    
                        raise ValidationError("El Producto %s no puede ser menor al precio %f"%(r.product_id.name,r.product_id.price_min))
                    if  r.lot_id and r.quantity>1:
                        raise ValidationError("Solo puede seleccionar una unidad de la serie %s del producto %s"%(r.lot_id.name,r.product_id.name))
                    if  r.qty_available==0 and record.type in ["out_invoice","in_refund"]:
                        raise ValidationError("No Hay unidades disponibles para el producto %s"%(r.product_id.name))
                    if r.product_id.tracking == "serial" and not r.lot_id:
                        raise ValidationError("Los productos con tipo de seguimiento 'SERIAL' debe tener un  número de serie asociado.")
    @api.multi
    def generar_nota_debito(self):
        if not self.number:
            self.action_invoice_open()
        ref = request.env.ref("account.invoice_form")
        
        #print( str(self.number[0:4]) + " - " + str(int(self.number[5:len(self.number)])))
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "target": "self",
            "view_id": ref.id,
            "view_mode": "form",
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_refund_invoice_id': self.id,
                'default_date_invoice': self.date_invoice,
                'default_payment_term_id': self.payment_term_id.id,
                'default_new_invoice': False,
                'type': 'out_invoice',
                'journal_type': 'sale',
                'type_code': '08',
                'default_number': 'Nota de Débito'},
            "domain": [('type', '=', 'out_invoice'), ('journal_id.invoice_type_code_id', '=', '08')]
        }

    @api.multi
    def generar_nota_credito(self):
        if not self.number:
            self.action_invoice_open()
        ref = request.env.ref("account.invoice_form")
        inv_lines2 = []
        for il1 in self.invoice_line_ids:
            obj = il1.copy(default={
                "invoice_id": ""
            })
            inv_lines2.append(obj.id)
        #print(str(self.number[0:4]) + " - " + str(int(self.number[5:len(self.number)])))
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "target": "self",
            "view_id": ref.id,
            "view_mode": "form",
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_refund_invoice_id': self.id,
                'default_date_invoice': self.date_invoice,
                'default_payment_term_id': self.payment_term_id.id,
                'default_invoice_line_ids': inv_lines2,
                'default_location_id':self.location_id.id,
                'default_new_invoice': False,
                'default_type': 'out_refund',
                'journal_type': 'sale',
                'type_code': '07',
                'default_number': 'Nota de Crédito'},
            "domain": [('type', '=','out_refund'), ('journal_id.invoice_type_code_id', '=', '07')]
        }

class AccountInvoiceLine(models.Model):
    _inherit = ['account.invoice.line']


    @api.constrains("price_unit")
    def restricion_precio(self):
        for record in self:
            if record.invoice_id.type != "in_invoice":
                if (record.price_unit-record.descuento_unitario )<record.product_id.price_min:    
                    raise ValidationError("El Producto %s no puede ser menor al precio %f"%(record.product_id.name,record.product_id.price_min))

    @api.onchange("price_unit","descuento_unitario")
    def restricion_precio2(self):
        for record in self:
            if record.invoice_id.type != "in_invoice":
                if (record.price_unit-record.descuento_unitario)<record.product_id.price_min:    
                    raise ValidationError("El Producto %s no puede ser menor al precio %f"%(record.product_id.name,record.product_id.price_min))

    location_id = fields.Many2one("stock.location")

    stock_quant_ids = fields.Many2many("stock.quant",compute="get_stock_quants")
    lot_ids = fields.Many2many("stock.production.lot",compute="get_stock_quants")

    @api.depends("product_id","location_id")
    def get_stock_quants(self):
        for record in self:
            if record.invoice_id.type in ['out_invoice','in_refund']:
                stock_quant_ids = record.env["stock.quant"].sudo().search([("location_id","=",record.location_id.id),("product_id","=",record.product_id.id)])
                if record.product_id.tracking=="serial":
                    lot_ids = [ sq.lot_id.id for sq in stock_quant_ids]
                    record.lot_ids = [(6,0,lot_ids)]
                stock_quant_ids = [sq.id for sq in stock_quant_ids]
                record.stock_quant_ids =  [(6,0,stock_quant_ids)]
            elif record.invoice_id.type in ["out_refund",'in_invoice']:
                stock_quant_ids = record.env["stock.quant"].sudo().search([("location_id","=",request.env.ref("stock.stock_location_customers").id),("product_id","=",record.product_id.id)])
                if record.product_id.tracking=="serial":
                    lot_ids = [ sq.lot_id.id for sq in stock_quant_ids]
                    record.lot_ids = [(6,0,lot_ids)]
                stock_quant_ids = [sq.id for sq in stock_quant_ids]
                record.stock_quant_ids =  [(6,0,stock_quant_ids)]
            
            if record.location_id and record.product_id:
                stock_quant_ids = self.env["stock.quant"].sudo().search([("location_id","=",record.location_id.id),("product_id","=",record.product_id.id)])
                qty = sum([sq.quantity for sq in stock_quant_ids])
                record.qty_available=qty
            else:
                record.qty_available=0

    lot_id = fields.Many2one("stock.production.lot")
    ref = fields.Char(related="lot_id.ref",default=False)
    qty_available = fields.Integer("Cantidad disponible",compute="get_stock_quants")

    """
    @api.depends("product_id","location_id")
    def _compute_qty_available(self):
        for record in self:
            if record.location_id and record.product_id:
                stock_quant_ids = self.env["stock.quant"].sudo().search([("location_id","=",record.location_id.id),("product_id","=",record.product_id.id)])
                qty = sum([sq.quantity for sq in stock_quant_ids])
                record.qty_available=qty
            else:
                record.qty_available=0
    """

    @api.onchange('product_id','lot_id')
    def _onchange_product_name(self):
        if self.product_id:
            self.name = self.product_id.name+(" Modelo: "+self.product_id.default_code if self.product_id.default_code else "")
            if self.lot_id:
                self.name = self.name +(" S/N: "+self.lot_id.name if self.lot_id.name else self.lot_id.name)+(" - "+self.lot_id.ref if self.lot_id.ref else "")
            