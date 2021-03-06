# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CorteMoviemintoLote(models.Model):
    _inherit = "stock.production.lot"
    
    @api.model
    def _get_default_warehouse(self):
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        return warehouse_id

    active = fields.Boolean(default=True)
    parent_id = fields.Many2one("stock.production.lot",string="Lote Principal")
    lotes_hijos = fields.One2many('stock.production.lot','parent_id',string='Lotes Hijos')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=_get_default_warehouse)
    picking_id = fields.Many2one('stock.picking', 'Orden de Salida', copy=False)

    def realizar_corte(self):
        view_form = self.env.ref("corte_lotes.view_form_corte_report_wizard")

        return {
            "type":"ir.actions.act_window",
            "view_mode":"form",
            "views_id":[(view_form.id,"form")],
            "target":"new",
            "res_model":"lot.corte.wizard",
            "context":{"default_parent_id":self.id,
                        "default_product_id":self.product_id.id,
                        "default_uom_id":self.product_uom_id.id,
                        "default_product_cantidad":self.product_qty}
        }

class CorteMovimientoLoteWizard(models.TransientModel):
    _name = "lot.corte.wizard"

    parent_id = fields.Many2one("stock.production.lot",string="Lote Principal")
    product_id = fields.Many2one("product.product",string="Producto")
    uom_id = fields.Many2one("product.uom",string="Unidad de Medida")
    product_cantidad = fields.Integer(string="Cantidad de Producto")
    cantidad_porciones = fields.Integer('Cantidad de Porciones')
    porciones_ids = fields.One2many('lineas.lot.corte.wizard','corte_line_id',string='Porciones')
    
    @api.onchange("cantidad_porciones")
    def generar_porciones(self):
        lines = [(6,0,[])]
        cont = 0
        for rec in self:
            if rec.cantidad_porciones > 1:
                while cont < rec.cantidad_porciones:
                    cont_display = cont + 1
                    nombre = "{}-{}".format(rec.parent_id.name,cont_display)
                    lines.append({"nombre_porcion":nombre,"cantidad":"0"})
                    cont += 1
            rec.porciones_ids = lines
            

    def ejecutar_corte(self):
        rec = self
        suma_cantidades = sum([line.cantidad for line in rec.porciones_ids])

        if suma_cantidades == rec.product_cantidad:

            if rec.product_id and rec.product_id.type != 'service':

                    referencia_salida = "{}-{}-Salida por Corte".format(rec.parent_id.warehouse_id.out_type_id.default_location_src_id.id,rec.parent_id.id)
                    referencia_entrada = "{}-{}-Entrada por Corte".format(rec.parent_id.warehouse_id.out_type_id.default_location_src_id.id,rec.parent_id.id)
                    stock_move = self.env["stock.move"].create({
                        'name': 'Salida por Corte',
                        'product_id': rec.parent_id.product_id.id,
                        'product_uom_qty': rec.parent_id.product_qty,
                        'product_uom': rec.parent_id.product_id.uom_id.id,
                        'date': fields.datetime.now(),
                        'date_expected': fields.datetime.now(),
                        'picking_type_id': rec.parent_id.warehouse_id.out_type_id.id,
                        'state': 'done',
                        'reference': referencia_salida,
                        'location_id': rec.parent_id.warehouse_id.out_type_id.default_location_src_id.id,
                        'location_dest_id': rec.parent_id.warehouse_id.out_type_id.default_location_dest_id.id,
                        #'quantity_done': line.quantity,
                    })
                    self.env["stock.move.line"].create({
                        'product_id': rec.product_id.id,
                        'product_uom_id': rec.parent_id.product_id.uom_id.id,
                        'reference': referencia_salida,
                        'move_id': stock_move.id,
                        'qty_done': rec.parent_id.product_qty,
                        'location_id': rec.parent_id.warehouse_id.out_type_id.default_location_src_id.id,
                        'location_dest_id': rec.parent_id.warehouse_id.out_type_id.default_location_dest_id.id,
                        'lot_id': rec.parent_id.id,
                        })

            for line in rec.porciones_ids:
                lote_id = self.env["stock.production.lot"].create({
                                        "name":line.nombre_porcion,
                                        "product_id":rec.product_id.id,
                                        "parent_id":rec.parent_id.id})

                if rec.product_id and rec.product_id.type != 'service':
                    stock_move = self.env["stock.move"].create({
                        'name': 'Ingreso por Corte',
                        'product_id': rec.parent_id.product_id.id,
                        'product_uom_qty': rec.parent_id.product_qty,
                        'product_uom': rec.parent_id.product_id.uom_id.id,
                        'date': fields.datetime.now(),
                        'date_expected': fields.datetime.now(),
                        'picking_type_id': rec.parent_id.warehouse_id.in_type_id.id,
                        'state': 'done',
                        'reference': referencia_entrada,
                        'location_id': rec.parent_id.warehouse_id.in_type_id.default_location_src_id.id,
                        'location_dest_id': rec.parent_id.warehouse_id.in_type_id.default_location_dest_id.id,
                        #'quantity_done': line.quantity,
                    })
                    self.env["stock.move.line"].create({
                        'product_id': rec.product_id.id,
                        'product_uom_id': rec.parent_id.product_id.uom_id.id,
                        'reference': referencia_entrada,
                        'move_id': stock_move.id,
                        'qty_done': line.cantidad,
                        'location_id': rec.parent_id.warehouse_id.in_type_id.default_location_src_id.id,
                        'location_dest_id': rec.parent_id.warehouse_id.in_type_id.default_location_dest_id.id,
                        'lot_id': lote_id.id,
                        })
                

    
class LineasLoteWizard(models.TransientModel):
    _name = "lineas.lot.corte.wizard"
    
    corte_line_id = fields.Many2one("lot.corte.wizard",string="Lote Principal")
    nombre_porcion = fields.Char('Nombre')
    cantidad = fields.Integer('Cantidad')