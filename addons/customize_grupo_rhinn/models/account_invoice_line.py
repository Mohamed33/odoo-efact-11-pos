# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo.http import request
from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import Warning
import os
import json
class SupplierInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if picking.type == 'out_invoice':
                pick = picking.picking_transfer_id.id
                location = line.invoice_id.picking_transfer_id.default_location_src_id.id
                des_location = line.invoice_id.partner_id.property_stock_customer.id
            else:
                pick = picking.picking_type_id.id
                des_location = line.invoice_id.picking_type_id.default_location_dest_id.id
                location = line.invoice_id.partner_id.property_stock_supplier.id
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
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
            """
            if line.lot_id:
                sml_id = self.env["stock.move.line"].create({"lot_name":line.lot_id.name,
                                                            'location_id': location,
                                                            'product_id':line.product_id.id,
                                                            'location_dest_id': des_location,
                                                            "lot_id":line.lot_id.id,
                                                            'picking_id': picking.id,
                                                            "product_uom_id":line.uom_id.id,
                                                            "product_uom_qty":1,
                                                            "qry_done":1,
                                                            "move_id":done.id})
                done.move_line_ids= [(6,0,[sml_id.id])]
            """
        return done

    def create_stock_moves_transfer(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if line.invoice_id.type == 'out_invoice':
                os.system("echo 'out_invoice' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = line.invoice_id.picking_transfer_id.default_location_src_id.id
                des_location = line.invoice_id.partner_id.property_stock_customer.id
            elif line.invoice_id.type == 'out_refund':
                os.system("echo 'out_refund' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = request.env.ref("stock.stock_location_customers").id
                des_location = line.invoice_id.picking_transfer_id.default_location_src_id.id
            elif line.invoice_id.type == 'in_refund':
                os.system("echo 'in_refund' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = request.env.ref("stock.stock_location_suppliers").id
                des_location = line.invoice_id.picking_transfer_id.default_location_src_id.id
            elif line.invoice_id.type == 'in_invoice':
                os.system("echo 'in_invoice' ")
                pick = picking.picking_type_id.id
                des_location = line.invoice_id.picking_type_id.default_location_dest_id.id
                location = line.invoice_id.partner_id.property_stock_supplier.id

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'location_id': location,
                'location_dest_id': des_location,
                'picking_id': picking.id,
                #'move_dest_id': False,
                'state': 'draft',
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': picking.picking_type_id.id,
                #'procurement_id': False,
                'route_ids': 1 and [
                    (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            diff_quantity = line.quantity
            tmp = template.copy()

            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            
            template['product_uom_qty'] = diff_quantity
            done = moves.create(template)
           
            if line.lot_id:

                sml_id = self.env["stock.move.line"].sudo().create({"lot_name":line.lot_id.name,
                                                            'location_id': location,
                                                            'product_id':line.product_id.id,
                                                            'location_dest_id': des_location,
                                                            "lot_id":line.lot_id.id,
                                                            'picking_id': picking.id,
                                                            "product_uom_id":line.uom_id.id,
                                                            "product_uom_qty":1,
                                                            "qty_done":1,
                                                            "move_id":done.id})
                stock_quant_lot = self.env["stock.quant"].search([("lot_id","=",line.lot_id.id)])
                if stock_quant_lot.exists():
                    stock_quant_lot.write({"reserved_quantity":1})

                done.move_line_ids= [(6,0,[sml_id.id])]

        return done