from odoo import api, fields, models

class ComboProduct(models.Model):
    _name = "product.combo"
    _description = "Product packs"

    
    @api.multi
    @api.onchange('product_id')
    def product_id_onchange(self):
        for record in self:
            if record.product_id:
                record.uom_id = record.product_id.uom_id.id

        return {'domain': {'product_id': [('is_combo', '=', False)]}}

    name = fields.Char('name')
    product_template_id = fields.Many2one('product.template', 'Item')
    product_quantity = fields.Float('Quantity', default='1', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    uom_id = fields.Many2one('product.uom')
    price = fields.Float('Product_price',related="product_id.list_price")
    price_subtotal = fields.Float(compute="_compute_price_subtotal",string="Sub-Total")
    free = fields.Boolean("Gratis?")

    @api.depends("free","product_quantity","product_id","price")
    def _compute_price_subtotal(self):
        for record in self:
            if not record.free and record.product_id.uom_id.factor_inv:
                record.price_subtotal = record.price*record.product_quantity*record.uom_id.factor_inv/record.product_id.uom_id.factor_inv
            else:
                record.price_subtotal = 0

class ComboProductTemplate(models.Model):
    _inherit = "product.template"

    is_combo = fields.Boolean('Combo Product', default=False)
    combo_product_id = fields.One2many('product.combo', 'product_template_id', 'Combo Item')

    price_combo_total = fields.Float(compute="_compute_price_combo_total")

    @api.depends("combo_product_id")
    def _compute_price_combo_total(self):
        for record in self:
            record.price_combo_total = sum([c.price_subtotal for c in record.combo_product_id])