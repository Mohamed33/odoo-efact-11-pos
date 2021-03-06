# -*- coding: utf-8 -*-
##########################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##########################################################################

from odoo import models, fields, api, _
from odoo.tools import float_is_zero


class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_qty = fields.Boolean(string='Display Stock')
    restrict_order = fields.Boolean(string='Restrict Order When Out Of Stock')
    prod_qty_limit = fields.Integer(string="Restrict When Product Qty Remains")
    custom_msg = fields.Char(string="Custom Message")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    picking_ids = fields.Many2many(
        "stock.picking",
        string="Multiple Picking",
        copy=False)

    @api.one
    def multi_picking(self):
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        address = self.partner_id.address_get(['delivery']) or {}
        picking_type = self.picking_type_id
        order_picking = Picking
        return_picking = Picking
        return_pick_type = self.picking_type_id.return_picking_type_id or self.picking_type_id
        message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (self.id, self.name)
        if self.partner_id:
            destination_id = self.partner_id.property_stock_customer.id
        else:
            if (not picking_type) or (
                    not picking_type.default_location_dest_id):
                customerloc, supplierloc = StockWarehouse._get_partner_locations()
                destination_id = customerloc.id
            else:
                destination_id = picking_type.default_location_dest_id.id
        lst_picking = []
        location_ids = list(set([line.location_id.id for line in self.lines]))
        for loc_id in location_ids:
            picking_vals = {
                'origin': self.name,
                'partner_id': address.get('delivery', False),
                'date_done': self.date_order,
                'picking_type_id': picking_type.id,
                'company_id': self.company_id.id,
                'move_type': 'direct',
                'note': self.note or "",
                'location_id': loc_id,
                'location_dest_id': destination_id,
            }
            pos_qty = any(
                [x.qty > 0 for x in self.lines if x.product_id.type in ['product', 'consu']])
            if pos_qty:
                order_picking = Picking.create(picking_vals.copy())
                order_picking.message_post(body=message)
            neg_qty = any(
                [x.qty < 0 for x in self.lines if x.product_id.type in ['product', 'consu']])
            if neg_qty:
                return_vals = picking_vals.copy()
                return_vals.update({
                    'location_id': destination_id,
                    'location_dest_id': loc_id,
                    'picking_type_id': return_pick_type.id
                })
                return_picking = Picking.create(return_vals)
                return_picking.message_post(body=message)
            for line in self.lines.filtered(
                lambda l: l.product_id.type in [
                    'product',
                    'consu'] and l.location_id.id == loc_id and not float_is_zero(
                    l.qty,
                    precision_digits=l.product_id.uom_id.rounding)):
                Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': loc_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else loc_id,
                })
            if return_picking:
                self.write({'picking_ids': [(4, return_picking.id)]})
                self._force_picking_done(return_picking)
            if order_picking:
                self.write({'picking_ids': [(4, order_picking.id)]})
                self._force_picking_done(order_picking)
        return True

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            # custom multi location
            multi_loc = False
            for line_order in order.lines:
                if line_order.location_id:
                    multi_loc = True
                    break
            if multi_loc:
                order.multi_picking()
            else:
                if not order.lines.filtered(
                    lambda l: l.product_id.type in [
                        'product', 'consu']):
                    continue
                address = order.partner_id.address_get(['delivery']) or {}
                picking_type = order.picking_type_id
                return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
                order_picking = Picking
                return_picking = Picking
                moves = Move
                location_id = order.location_id.id
                if order.partner_id:
                    destination_id = order.partner_id.property_stock_customer.id
                else:
                    if (not picking_type) or (
                            not picking_type.default_location_dest_id):
                        customerloc, supplierloc = StockWarehouse._get_partner_locations()
                        destination_id = customerloc.id
                    else:
                        destination_id = picking_type.default_location_dest_id.id

                if picking_type:
                    message = _(
                        "This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                    picking_vals = {
                        'origin': order.name,
                        'partner_id': address.get('delivery', False),
                        'date_done': order.date_order,
                        'picking_type_id': picking_type.id,
                        'company_id': order.company_id.id,
                        'move_type': 'direct',
                        'note': order.note or "",
                        'location_id': location_id,
                        'location_dest_id': destination_id,
                    }
                    pos_qty = any(
                        [x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                    if pos_qty:
                        order_picking = Picking.create(picking_vals.copy())
                        order_picking.message_post(body=message)
                    neg_qty = any(
                        [x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                    if neg_qty:
                        return_vals = picking_vals.copy()
                        return_vals.update({
                            'location_id': destination_id,
                            'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                            'picking_type_id': return_pick_type.id
                        })
                        return_picking = Picking.create(return_vals)
                        return_picking.message_post(body=message)

                    for line in order.lines.filtered(
                        lambda l: l.product_id.type in [
                            'product', 'consu'] and not float_is_zero(
                            l.qty, precision_digits=l.product_id.uom_id.rounding)):
                        moves |= Move.create({
                            'name': line.name,
                            'product_uom': line.product_id.uom_id.id,
                            'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                            'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': abs(line.qty),
                            'state': 'draft',
                            'location_id': location_id if line.qty >= 0 else destination_id,
                            'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        })

                    # prefer associating the regular order picking, not the
                    # return
                    order.write(
                        {'picking_id': order_picking.id or return_picking.id})

                    if return_picking:
                        order._force_picking_done(return_picking)
                    if order_picking:
                        order._force_picking_done(order_picking)

                # when the pos.config has no picking_type_id set only the moves
                # will be created
                if moves and not return_picking and not order_picking:
                    tracked_moves = moves.filtered(
                        lambda move: move.product_id.tracking != 'none')
                    untracked_moves = moves - tracked_moves
                    tracked_moves.action_confirm()
                    untracked_moves.action_assign()
                    moves.filtered(
                        lambda m: m.state in [
                            'confirmed',
                            'waiting']).force_assign()
                    moves.filtered(
                        lambda m: m.product_id.tracking == 'none').action_done()

        return True


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    location_id = fields.Many2one('stock.location', string='Location')


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def disp_prod_stock(self, product_id, shop_id):
        stock_line = []
        total_qty = 0
        shop_qty = 0
        quant_obj = self.env['stock.quant']
        for warehouse_id in self.search([]):
            product_qty = 0.0
            ware_record = warehouse_id
            location_id = ware_record.lot_stock_id.id
            if shop_id:
                loc_ids1 = self.env['stock.location'].search(
                    [('location_id', 'child_of', [shop_id])])
                stock_quant_ids1 = quant_obj.search([('location_id', 'in', [
                                                    loc_id.id for loc_id in loc_ids1]), ('product_id', '=', product_id)])
                for stock_quant_id1 in stock_quant_ids1:
                    shop_qty = stock_quant_id1.quantity

            loc_ids = self.env['stock.location'].search(
                [('location_id', 'child_of', [location_id])])
            stock_quant_ids = quant_obj.search([('location_id', 'in', [
                                               loc_id.id for loc_id in loc_ids]), ('product_id', '=', product_id)])
            for stock_quant_id in stock_quant_ids:
                product_qty += stock_quant_id.quantity
            stock_line.append([ware_record.name, product_qty,
                               ware_record.lot_stock_id.id])
            total_qty += product_qty
        return stock_line, total_qty, shop_qty
