# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Create Stock Picking/Stock Move from Invoice/Refund',
    'version': '11.0.0.3',
    'category': 'Warehouse',
    'summary': 'This apps helps to generate stock move or stock picking from invoice',
    'description': """
    This module helps to create a stock move and picking while validating a invoice.
    Create Stock Picking from Invoice
    Create Stock Move from Invoice
    Create Picking from Invoice
    Create Stock Picking and Stock Move from Invoice
    Create Stock Picking from Invoice refund
    Create Stock Move from Invoice refund
    Create Stock Picking from refund
    Create Stock Move from refund
    Create Picking from Invoice
    Create Move from Invoice

     Création de stock picking à partir de la facture
     Créer un mouvement de stock à partir de la facture
     Créer une cueillette à partir d'une facture
     Création de stock picking et de stock à partir de la facture
     Création de stock picking à partir du remboursement de facture
     Créer un mouvement de stock à partir du remboursement de facture
     Créer un stock picking à partir du remboursement
     Créer Stock Move à partir du remboursement
     Créer une cueillette à partir d'une facture
     Créer un mouvement à partir de la facture

     Crear Stock Picking from Invoice
     Crear Stock Move from Invoice
     Crear Picking de Factura
     Crear Stock Picking y Stock Move from Invoice
     Crear Stock Picking from Invoice refund
     Crear Stock Move from Invoice refund
     Crear Stock Picking from refund
     Crear Stock Mover de reembolso
     Crear Picking de Factura
     Crear mover de la factura
""",
    'author': 'BrowseInfo',
    'price': '15',
    'currency': "EUR",
    'website': 'http://www.browseinfo.in',
    'images': [],
    'depends': ['account_invoicing','stock', 'purchase','sale_management',"efact"],
    'data': [
        'views/account_invoice_view.xml',
        'security/ir.model.access.csv',
    ],
    'live_test_url':'https://www.youtube.com/watch?v=gf6cA-dixUE&feature=youtu.be',
    'installable': True,
    'auto_install': False,
    'application': True,
    'images':['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
