# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, fields, api, _
from collections import namedtuple

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    remaining_qty = fields.Float("Remaining Qty", compute="_compute_remaining_qty")

    def _compute_remaining_qty(self):
        for each in self:
            each.remaining_qty = 0
            for quant_id in each.quant_ids:
                if quant_id and quant_id.location_id and quant_id.location_id.usage == 'internal':
                    each.remaining_qty += quant_id.quantity
        return

    @api.model
    def get_qty_location(self, product_id=False, location_id=False):
        quant_ids = self.env['stock.quant'].search([]).filtered(lambda quant: quant.quantity > 0 and quant.location_id.id == location_id and quant.product_id.id == product_id)
        qty = 0.0
        lst_dict = []
        for quant in quant_ids:
            # qty+=quant.qty
            lst_dict.append({
                    'id':quant.lot_id.id,
                    'remaining_qty':quant.quantity,
                    'name':quant.lot_id.name,
                    'ref': quant.lot_id.ref,
                    'create_date': quant.lot_id.create_date,
                    'product_id': [quant.lot_id.product_id.id, quant.lot_id.product_id.display_name]})
        return lst_dict

"""
class procurement_order(models.Model):
    _inherit = 'procurement.order'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.model
    def _get_stock_move_values(self):
        res = super(
            procurement_order, self)._get_stock_move_values()
        res['restrict_lot_id'] = self.lot_id.id
        return res
"""

class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.multi
    def _prepare_procurement_from_move(self):
        self.ensure_one()
        vals = super(StockMove, self)._prepare_procurement_from_move()
        vals['lot_id'] = self.restrict_lot_id.id
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: