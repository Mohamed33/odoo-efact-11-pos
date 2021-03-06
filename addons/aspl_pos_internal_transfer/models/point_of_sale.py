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

from openerp import models,fields,api,_
# 
class pos_config(models.Model):
    _inherit = 'pos.config'
    
    enable_int_trans_stock = fields.Boolean(string="Internal Stock Transfer")

class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def do_detailed_internal_transfer(self, vals):
        move_lines = [] 
        if vals and vals.get('data'):
            for move_line in vals.get('data').get('moveLines'):
                move_lines.append((0,0,move_line))
            picking_vals = {'location_id': vals.get('data').get('location_src_id'),
                            'state':'draft', 
                            'move_lines': move_lines,
                            'location_dest_id': vals.get('data').get('location_dest_id'),
                            'picking_type_id': vals.get('data').get('picking_type_id')}
            picking_id = self.create(picking_vals)
            if picking_id:
                if vals.get('data').get('state') == 'confirmed':
                    picking_id.action_confirm()
                if vals.get('data').get('state') == 'done':
                    picking_id.action_confirm()
                    picking_id.force_assign()
                    picking_id.button_validate()
                    stock_transfer_id = self.env['stock.immediate.transfer'].search([('pick_ids', '=', picking_id.id)], limit=1).process()
                    if stock_transfer_id:
                        stock_transfer_id.process()
        return [picking_id.id,picking_id.name]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: