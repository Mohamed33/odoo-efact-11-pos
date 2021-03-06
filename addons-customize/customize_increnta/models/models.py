# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import os
import json

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    transferencia_interna_virtual = fields.Boolean("Transferencia Interna Virtual",default=False,copy=False)
    ubicacion_final = fields.Many2one("stock.location",string="Ubicación Final",copy=False)
    validar_stock_disponible = fields.Boolean("Validar stock disponible en las líneas",default=False)

    @api.onchange('code')
    def _onchange_code(self):
        for record in self:
            if record.code != 'internal':
                record.transferencia_interna_virtual = False
                record.ubicacion_final = False

    @api.onchange('transferencia_interna_virtual')
    def _onchange_transferencia_interna_virtual(self):
        for record in self:
            if not record.transferencia_interna_virtual:
                record.ubicacion_final = False
                record.default_location_dest_id = False
            else:
                record.default_location_dest_id = self.env.ref("stock.location_inventory").id


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    es_producto_maestro = fields.Boolean("Es producto maestro",default = False,related="product_tmpl_id.es_producto_maestro")
    producto_maestro_referencia_id = fields.Many2one("product.product",string="Producto maestro de referencia",related="product_tmpl_id.producto_maestro_referencia_id")

    
    @api.constrains('producto_maestro_referencia_id')
    def _check_producto_maestro_referencia_id(self):
        for record in self:
            if record.es_producto_maestro and record.producto_maestro_referencia_id:
                raise UserError("Un Producto maestro no puede tener un Producto maestro de referencia.")

    
    @api.onchange("es_producto_maestro")
    def _onchange_es_producto_maestro(self):
        for record in self:
            if record.es_producto_maestro:
                record.producto_maestro_referencia_id = False
                

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    es_producto_maestro = fields.Boolean("Es producto maestro",default = False,copy=False)
    producto_maestro_referencia_id = fields.Many2one("product.product",string="Producto maestro de referencia",copy=False)

    
    @api.constrains('producto_maestro_referencia_id')
    def _check_producto_maestro_referencia_id(self):
        for record in self:
            if record.es_producto_maestro and record.producto_maestro_referencia_id:
                raise UserError("Un Producto maestro no puede tener un Producto maestro de referencia.")

    
    @api.onchange("es_producto_maestro")
    def _onchange_es_producto_maestro(self):
        for record in self:
            if record.es_producto_maestro:
                record.producto_maestro_referencia_id = False
                
class StockMove(models.Model):
    _inherit = "stock.move"
    picking_id2 = fields.Many2one("stock.picking")


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    transferencia_interna_virtual = fields.Boolean(string="Transferencia Interna Virtual",copy=False)
    ubicacion_final = fields.Many2one("stock.location",string="Ubicación Final",copy=False)
    move_lines2 = fields.One2many("stock.move","picking_id2",copy=False)

    @api.onchange("transferencia_interna_virtual")
    def _onchange_transferencia_interna_virtual(self):
        for record in self:
            if record.transferencia_interna_virtual:
                picking_type_ids = self.env["stock.picking.type"].search([['transferencia_interna_virtual',"=",True]])
                if len(picking_type_ids)>0:
                    record.picking_type_id = picking_type_ids[0].id

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for record in self:
            if record.transferencia_interna_virtual:
                record.ubicacion_final = record.picking_type_id.ubicacion_final.id

    """
    @api.model
    def create(self, vals):
        os.system("echo 'create lines'")
        os.system("echo '{}'".format(self.picking_type_id.validar_stock_disponible))
        if self.picking_type_id.validar_stock_disponible:
            os.system("echo '{}'".format(len(self.move_lines)))
            for line in self.move_lines:
                os.system("echo '{}, {}'".format(line.product_id.name,line.product_id.qty_available))
                if line.product_id.qty_available < line.quantity_done:
                    raise UserError("No hay cantidad disponible para el producto {}, (cantidad disponible {})".format(line.product_id.name,line.product_id.qty_available))

        
        res = super(StockPicking, self).create(vals)
        return res
    """
    def action_confirm(self):
        self.move_lines2._action_confirm(merge=False)
        return super(StockPicking,self).action_confirm()

    @api.multi
    def action_done(self):
        self.move_lines2._action_done()
        return super(StockPicking,self).action_done()



    @api.onchange("move_lines","move_lines.product_id","move_lines.quantity_done")
    def _onchange_move_lines(self):
        for record in self:
            if record.transferencia_interna_virtual:
                productos_maestros = {}
                move_lines = []
                for line in record.move_lines:
                    product = line.product_id
                    product_maestro = product.producto_maestro_referencia_id
                    if product_maestro:
                        if str(product_maestro.id) in productos_maestros:
                            productos_maestros[str(product_maestro.id)] = (product_maestro,productos_maestros[str(product_maestro.id)][1]+line.quantity_done)
                        else:
                            productos_maestros[str(product_maestro.id)] = (product_maestro,line.quantity_done)

                productos_maestros_list = list(productos_maestros.values())
                for p in productos_maestros_list:
                    #if p[0].id not in [ml["product_id"] for ml in move_lines]:
                    move_lines.append({
                        "name":record.product_id.name,
                        "date_expected":record.scheduled_date,
                        "product_id":p[0].id,
                        "product_type":p[0].type,
                        "quantity_done":p[1],
                        "picking_type_id":record.picking_type_id.id,
                        "location_id":record.location_dest_id.id,
                        "location_dest_id":record.ubicacion_final.id,
                        "product_uom":p[0].uom_id.id,
                        "state":"draft",
                        "scrapped":record.ubicacion_final.scrap_location,
                        "picking_id2":record.id,
                        "product_uom_qty":p[1]
                    })
                    """
                    template = {
                        'name': line.name or '',
                        'product_id': line.product_id.id,
                        'product_uom': line.uom_id.id,
                        'location_id': location,
                        'location_dest_id': des_location,
                        'move_dest_id': False,
                        'state': 'draft',
                        'invoice_id':picking.id,
                        'company_id': line.invoice_id.company_id.id,
                        'price_unit': price_unit,
                        'picking_type_id': pick,
                        'procurement_id': False,
                        'route_ids': 1 and [
                            (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                        'warehouse_id': picking.picking_type_id.warehouse_id.id,
                    }
                    """

                    """
                    else:
                        for ml in move_lines:
                            if p[0].id == ml["product_id"]:
                                ml["quantity_done"] = p[1]
                    """

                record.move_lines2 = move_lines
