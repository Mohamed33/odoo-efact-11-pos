
from openerp import api, models
from odoo.tools.profiler import profile

class ComboSaleOrder(models.Model):
    _inherit = "sale.order"
    """
    @api.multi
    @profile
    def action_confirm(self):
        res = super(ComboSaleOrder, self).action_confirm()
        pickings_id = self.picking_ids
        picking_lines = []
        for line in self.order_line:
            if line.product_id.combo_product_id:
                for pack_id in line.product_id.combo_product_id:
                    qty = pack_id.product_quantity * line.product_uom_qty
                    picking_lines.append((0, 0, {
                        'name': pack_id.product_id.name,
                        'product_id': pack_id.product_id.id,
                        'product_uom_qty': qty,
                        'picking_id': pickings_id.id,
                        'product_uom': pack_id.uom_id.id,
                        'location_id': pickings_id.move_lines[0].location_id.id,
                        'location_dest_id': pickings_id.move_lines[0].location_dest_id.id,
                        'state': 'draft'}))
        pickings_id.move_lines = picking_lines
        #pickings_id.action_assign()
        for move in pickings_id.move_lines:
            move._action_assign()
            move.filtered(lambda m: m.state in ['confirmed', 'waiting'])._force_assign()
            move.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
        return res

    """
    @api.multi
    def action_confirm(self):
        res = super(ComboSaleOrder, self).action_confirm()
        #return res
        #print([(x.name,x.state) for x in self.picking_ids])
        pickings_ids = self.picking_ids.filtered(lambda m: m.state in ['confirmed', 'waiting','done','assigned'])
        #print([x.name for x in pickings_ids])
        for pickings_id in pickings_ids:
            picking_lines = []
            for line in self.order_line:
                if line.product_id.combo_product_id:
                    for pack_id in line.product_id.combo_product_id:
                        qty = round(pack_id.product_quantity * line.product_uom_qty,0)
                        picking_lines.append((0, 0, {
                                                'name': pack_id.product_id.name,
                                                'product_id': pack_id.product_id.id,
                                                'product_uom_qty': qty,
                                                #'quantity_done': qty,
                                                'picking_id': pickings_id.id,
                                                'product_uom': pack_id.uom_id.id,
                                                'location_id': pickings_id.move_lines[0].location_id.id,
                                                'location_dest_id': pickings_id.move_lines[0].location_dest_id.id,
                                                'state': 'draft'}))
            pickings_id.move_lines = picking_lines
            pickings_id.action_assign()
            for move in pickings_id.move_lines:
                move._action_assign()
                move.filtered(lambda m: m.state in ['confirmed', 'waiting'])._force_assign()
                move.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
        return res
    