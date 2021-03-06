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
{
    'name': 'POS Customer Credit And Debt Payment',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Point of Sale',
    'summary': 'POS Reorder, Reprint, Partial Payment, Customer Credit',
    'description': """ This module is mainly used to do the partial payment for POS orders and payment using
customer credit eg.Lets say, a customer comes to the shop and purchases products total of $200
but he wants to pay only $100 as partial payment and the remaining due amount the next day. 
as well as POS Reorder, Reprint. """,
    'website': 'http://www.acespritech.com',
    'depends': ['sale', 'point_of_sale', 'sale_management'],
    'price': 60.00,
    'currency': 'EUR',
    'images': [
        'static/description/main_screenshot.png',
    ],
    'data': [
        'views/aces_pos_partial.xml',
        'views/point_of_sale.xml',
        'views/pos_order_view.xml',
        'data/product.xml',
    ],
     'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/pos_credit.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
