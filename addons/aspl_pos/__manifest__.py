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
    'name': "ASPL POS",
    'version': '1.1',
    'category': 'Point of Sale',
    'description': """
This module allow user to return products, create sale order from pos, create or update product information.
""",
    'summary': 'several functionality within one module ASPL POS.',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': "http://www.acespritech.com",
    'currency': 'EUR',
    'price': 0.00,
    'depends': ['sale', 'point_of_sale', 'account'],
    'data': [
        'views/report_invoice_new.xml',
        'views/aspl_pos.xml',
        'views/point_of_sale_view.xml',
        'wizard/wizard_report_sale_journal_view.xml'
    ],
    'qweb': ['static/src/xml/pos.xml'],
    "installable": True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: