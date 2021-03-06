# -*- coding: utf-8 -*-

from odoo import models, fields

class pos_config(models.Model):
    _inherit = 'pos.config' 

    payment_sc = fields.Char('Payment')
    change_user_sc = fields.Char("Change user")
    change_customer_sc = fields.Char("Change Customer")
    select_search_box_sc = fields.Char("Select search box")
    add_new_order_sc = fields.Char("Add new order")
    remove_order_sc = fields.Char("Remove order")
    set_customer_sc = fields.Char("Set customer")
    qty_select_sc = fields.Char("Quantity select")
    dis_select_sc = fields.Char("Discount Select")
    price_select_sc = fields.Char("Price select")
    back_button_sc = fields.Char("Back Button")
    cancel_button_sc = fields.Char("Cancel Button")
    next_order_sc = fields.Char("Next Order")
    remove_order_line_sc = fields.Char("Remove order line")

class account_journal(models.Model):
    _inherit = 'account.journal' 

    payment_meth_sc = fields.Char("Payment Method shortcut")

class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement' 

    payment_meth_sc = fields.Char("Payment Method shortcut" , store=True, related='journal_id.payment_meth_sc')





    

