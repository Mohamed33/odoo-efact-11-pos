from odoo import fields,api,models
from odoo.addons import decimal_precision as dp

class PosOrderInvoiceLine(models.TransientModel):
    _name = "wizard.posorder.invoice.line"
    
    wizard_posorder_id = fields.Many2one("wizard.posorder.invoice")
    company_id = fields.Many2one("res.company",related="wizard_posorder_id.company_id")
    product_id = fields.Many2one("product.product")
    qty = fields.Float("Cantidad",digits=dp.get_precision('Product Unit of Measure'))
    price_unit = fields.Float("Precio Unitario",digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float("Subtotal",digits=dp.get_precision("Product Price"))
    tax_ids = fields.Many2many("account.tax")
    discount = fields.Float("Descuento",digits=dp.get_precision('Product Price'))
    uom_id = fields.Many2one("product.uom")

class WizardPosOrderInvoice(models.TransientModel):
    _name = "wizard.posorder.invoice"

    company_id = fields.Many2one("res.company",default=lambda self:self.env.user.company_id.id)
    pos_order_ids = fields.Many2many("pos.order")
    line_ids = fields.One2many("wizard.posorder.invoice.line","wizard_posorder_id")
    amount_total = fields.Float("Total", compute="_compute_amount_total")

    @api.depends("line_ids")
    def _compute_amount_total(self):
        for record in self:
            total = 0
            for line in record.line_ids:
                total += line.price_unit*line.qty
            record.amount_total = total

    @api.onchange("pos_order_ids")
    def _compute_lines(self):
        lines = {}
        self.line_ids = [(6,0,[])]
        for order in self.pos_order_ids:
            for line in order.lines:
                if line.qty>0:
                    if not lines.get(line.product_id):
                        lines[line.product_id] = {
                            "product":line.product_id,
                            "product_id":line.product_id.id,
                            "qty":line.qty,
                            "price_unit":line.price_unit,
                            "price_subtotal":line.qty*line.price_unit
                        }
                    else:
                        qty_acum = lines[line.product_id]["qty"]
                        price_unit_acum = lines[line.product_id]["price_unit"]

                        qty_total = qty_acum + line.qty
                        price_unit_avg = (qty_acum*price_unit_acum+ line.qty*line.price_unit)/qty_total

                        lines[line.product_id] = {
                            "product":line.product_id,
                            "product_id":line.product_id.id,
                            "qty":qty_total,
                            "price_unit":price_unit_avg,
                            "price_subtotal":qty_total*price_unit_avg
                        }
        
        res = []
        for line in lines:
            obj = lines[line]
            res.append({
                "product_id":obj["product_id"],
                "name":line.name,
                "qty":obj["qty"],
                "price_unit":obj["price_unit"],
                "price_subtotal":obj["price_subtotal"],
                "uom_id":line.uom_id.id,
                "tax_ids":[(6,0,[tax.id for tax in line.taxes_id])]
            })
        self.line_ids = res

    def action_create_invoice_factura(self):
        view_form_id = self.env.ref("account.invoice_form").id
        invoice_line_ids = []
        
        for line in self.line_ids:
            account_id = line.product_id.categ_id.property_account_income_categ_id or line.product_id.property_account_income_id
            invoice_line_ids.append({
                "product_id":line.product_id.id,
                "name":line.product_id.name,
                "quantity":line.qty,
                "uom_id":line.uom_id.id,
                "price_unit":line.price_unit,
                "invoice_line_tax_ids":[(6,0,[tax.id for tax in line.tax_ids])],
                "account_id":account_id.id
            })
        action = {
            "type":"ir.actions.act_window",
            "res_model":"account.invoice",
            "view_mode":"form",
            "target":"self",
            "views":[(view_form_id,"form")],
            "context":{
                "default_invoice_type_code":'01',
                "default_invoice_line_ids":invoice_line_ids
            }
        }

        return action
    
    def action_create_invoice_boleta(self):
        view_form_id = self.env.ref("account.invoice_form").id
        invoice_line_ids = []
        
        for line in self.line_ids:
            account_id = line.product_id.categ_id.property_account_income_categ_id or line.product_id.property_account_income_id
            invoice_line_ids.append({
                "product_id":line.product_id.id,
                "name":line.product_id.name,
                "quantity":line.qty,
                "uom_id":line.uom_id.id,
                "price_unit":line.price_unit,
                "invoice_line_tax_ids":[(6,0,[tax.id for tax in line.tax_ids])],
                "account_id":account_id.id
            })
        action = {
            "type":"ir.actions.act_window",
            "res_model":"account.invoice",
            "view_mode":"form",
            "target":"self",
            "views":[(view_form_id,"form")],
            "context":{
                "default_invoice_type_code":'03',
                "default_invoice_line_ids":invoice_line_ids
            }
        }

        return action