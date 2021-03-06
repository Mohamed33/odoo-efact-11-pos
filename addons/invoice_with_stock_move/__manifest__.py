# -*- encoding: utf-8 -*-
###########################################################################
#
#    Copyright (C) 2016 - Today Turkesh Patel. <http://www.almightycs.com>
#
#    @author Turkesh Patel <info@almightycs.com>
###########################################################################

{
    'name': 'Create Stock Moves With Invoice And Refunds',
    'category': 'Accounting',
    'version': '1.0.2',
    'author' : 'Almighty Consulting Services',
    'support': 'info@almightycs.com',
    'website' : 'http://www.almightycs.com',
    'summary': """Update Stock Automatically when validate Invoice And Refunds.""",
    'description': """Update Stock Automatically when validate Invoice And Refunds.
    change stock on refund stock move on refund picking with invoice with picking
    update stock on refund stock updatation on invoice update stock on invoice stock moves on invoice
    create piking on invoice 
    """,
    'depends': ['account_invoicing', 'stock'],
    'data': [
        'views/invoice_view.xml',
    ],
    'images': [
        'static/description/stock_move_invoice_turkeshpatel_almightycs_odoo.png',
    ],
    'installable': True,
    'auto_install': False,
    'price': 37,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
