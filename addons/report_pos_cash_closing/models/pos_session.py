from odoo import models, fields

class PosSession(models.Model):
    _inherit = "pos.session"

    def detalle_venta(self):
        pos_orders = self.env["pos.order"].search([("session_id","=",self.id)])
        sales_without_invoice = pos_orders.filtered(lambda po:not po.invoice_id)
        invoices = pos_orders.mapped("invoice_id")
        sales_refund = pos_orders.filtered(lambda po:po.amount_total<0)
 
        total_sales_without_invoice = sum([sale.amount_total for sale in sales_without_invoice])
        total_invoices = sum([inv.amount_total for inv in invoices])
        total_sales_refund = sum([sale.amount_total for sale in sales_refund])

        cash_start = self.cash_register_balance_start
        cash_end = self.cash_register_balance_start
        cash = self.statement_ids.filtered(lambda st:st.journal_id.type =="cash").line_ids

        sale_cash = cash.filtered(lambda ln:ln.pos_statement_id and ln.amount>0)
        refund_sale_cash = cash.filtered(lambda ln:ln.pos_statement_id  and ln.amount<0)
        in_cash = cash.filtered(lambda ln:not ln.pos_statement_id and ln.amount>0)
        out_cash = cash.filtered(lambda ln:not ln.pos_statement_id and ln.amount<0)

        total_sale_cash = sum([s.amount for s in sale_cash])
        total_refund_sale_cash = sum([s.amount for s in refund_sale_cash])
        total_in_cash = sum([s.amount for s in in_cash])
        total_out_cash = sum([s.amount for s in out_cash])

        return {"total_sales_without_invoice":total_sales_without_invoice,"total_invoices": total_invoices,"total_sales_refund":total_sales_refund,
                "cash_start":cash_start,"cash_end":cash_end,"total_sale_cash":total_sale_cash,"total_in_cash":total_in_cash,"total_out_cash":total_out_cash,
                "total_refund_sale_cash":total_refund_sale_cash,"in_cash":in_cash,"out_cash":out_cash,"sales_refund":sales_refund}

