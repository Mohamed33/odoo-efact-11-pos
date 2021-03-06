from odoo import api,models,fields
import os
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    es_facturable = fields.Boolean("Facturable",default=True)

    @api.onchange('partner_id')
    def _onchange_tipo_documento_cliente(self):
        for record in self:
            if record.partner_id.tipo_documento == '6':
                record.tipo_documento = '01'
            else:
                record.tipo_documento = '03'


    @api.multi
    def _action_confirm(self):
        for line in self.order_line:
            cantidad_disponible = line.product_id.virtual_available
            cantidad_pedida = line.product_uom_qty*line.product_uom.factor_inv/line.product_id.uom_id.factor_inv
            if cantidad_pedida>cantidad_disponible:
                raise ValidationError("* No se cuenta con la cantidad pedida para el producto %s,la cantidad disponible es %s %s"%(line.name,cantidad_disponible,line.product_id.uom_id.name))
        super(SaleOrder, self)._action_confirm()
        for order in self:
            for pick in order.picking_ids:
                if pick.state == 'assigned':
                    for move in pick.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                    pick.action_done()  