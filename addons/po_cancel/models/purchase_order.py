from odoo import api, fields, models,exceptions


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_cancel(self):
        quant_obj = self.env['stock.quant']
        model_obj = self.env['ir.model']
        moves = self.env['account.move']
        account_move_obj = self.env['account.move']
        model = model_obj.search([('model', '=', 'stock.landed.cost')])

        for order in self:
            if order.picking_ids and order.company_id.cancel_delivery_order_for_po :
                for picking in order.picking_ids:

                    if picking.state == 'cancel':
                        continue
                    if model and picking.picking_type_code == 'incoming':
                        cost_recs = self.env['stock.landed.cost'].search([('state', '=', 'done'),('picking_ids', 'in', order.picking_ids.ids)])
                        if cost_recs:
                            raise exceptions.Warning('Please Remove stock landed cost "%s" related with this incoming shipment(%s) then try to cancel it.'%(','.join(cost_recs.mapped('name')),picking.name))
                    if picking.state not in ['done']:
                        picking.action_cancel()
                    else:
                        account_moves=picking.move_lines

                        for move in account_moves:
                            if move.state == 'cancel':
                                continue
                            # move._do_unreserve()
                            if move.state == "done" and move.product_id.type == "product":
                                for move_line in move.move_line_ids:
                                    quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                                    quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity)
                                    quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id, quantity * -1)
                            if move.procure_method == 'make_to_order' and not move.move_orig_ids:
                                move.state = 'waiting'
                            elif move.move_orig_ids and not all(orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                                move.state = 'waiting'
                            else:
                                move.state = 'confirmed'
                            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                            if move.propagate:
                                # only cancel the next move if all my siblings are also cancelled
                                if all(state == 'cancel' for state in siblings_states):
                                    move.move_dest_ids._action_cancel()
                            else:
                                if all(state in ('done', 'cancel') for state in siblings_states):
                                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                                move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                            account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                            if account_moves:
                                for account_move in account_moves:
                                    account_move.button_cancel()
                                    account_move.unlink()

            if order.company_id.cancel_invoice_for_po:
                for invoice in order.invoice_ids:
                    if invoice.journal_id and not invoice.journal_id.update_posted:
                        invoice.journal_id.write({'update_posted':True})
                    if invoice.state in ['draft','open']:
                        invoice.action_cancel()

                    else:
                        moves = invoice.move_id
                        invoice.payment_move_line_ids.remove_move_reconcile()
                        # invoice.payment_move_line_ids.button_cancel()
                        if moves and not moves.journal_id.update_posted:
                            moves.write({'update_posted':True})
                        invoice.action_cancel()

        res = super(PurchaseOrder,self).button_cancel()
        return res
