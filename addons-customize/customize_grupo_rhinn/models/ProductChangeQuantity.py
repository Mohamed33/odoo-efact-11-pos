
from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = "product.template"

    stock_by_location = fields.Char("Stock por Ubicación",compute="_compute_stock_by_location")

    def _compute_stock_by_location(self):
        for record in self:
            stock_quant_ids = record.env["stock.quant"].search([("product_id","=",record.id)])

            stock_by_location = {}
            
            for loc in stock_quant_ids:
                if loc.location_id.usage=='internal':
                    if not loc.location_id.display_name in stock_by_location:
                        stock_by_location[loc.location_id.display_name]=loc.quantity
                    else:
                        stock_by_location[loc.location_id.display_name]+=loc.quantity
            
            stock_by_location_str = ""
            for loc in stock_by_location:
                stock_by_location_str+="* "+loc+":"+str(int(stock_by_location[loc]))+" ; "
            
            record.stock_by_location = stock_by_location_str



class ProductChangeQuantityLines(models.TransientModel):
    _name = "stock.change.product.qty.lines"
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', domain="[('product_id','=',product_id)]")
    ref = fields.Char("Código", related='lot_id.ref')
    product_id = fields.Many2one("product.product")
    new_quantity = fields.Float(
        'Cantidad', default=1,
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        help='This quantity is expressed in the Default Unit of Measure of the product.')
    
    product_change_qty_id = fields.Many2one("stock.change.product.qty")

class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    product_change_qty_lines_ids = fields.One2many("stock.change.product.qty.lines","product_change_qty_id")
    new_quantity = fields.Float(
        'New Quantity on Hand', default=1,
        digits=dp.get_precision('Product Unit of Measure'), 
        help='This quantity is expressed in the Default Unit of Measure of the product.')


    @api.multi
    def _prepare_inventory_line2(self,new_quantity,lot_id):
        product = self.product_id.with_context(location=self.location_id.id, lot_id=lot_id.id)
        th_qty = product.qty_available

        res = {
               'product_qty': new_quantity,
               'location_id': self.location_id.id,
               'product_id': self.product_id.id,
               'product_uom_id': self.product_id.uom_id.id,
               'theoretical_qty': th_qty,
               'prod_lot_id': lot_id.id,
        }

        return res

    @api.multi
    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']
        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            lines = []
            if wizard.product_id.tracking == "serial":
                for qty in wizard.product_change_qty_lines_ids:
                    lines.append((0,0,wizard._prepare_inventory_line2(qty.new_quantity,qty.lot_id)))
            else:
                lines = [(0,0,wizard._action_start_line())]

            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'
            
            print(lines)
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'line_ids': lines,
            })
            inventory.action_done()
        return {'type': 'ir.actions.act_window_close'}