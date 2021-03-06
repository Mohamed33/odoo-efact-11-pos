# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Vehícle",
    "version" : "11.0.0.1",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale','pos_journal_sequence','pos_orders_reprint'],
    "author": "Daniel Moreno",
    'summary': '',
    "description": """
    """,
    "website" : "",
    "data": [
        "views/views.xml",
        "views/view_assets.xml",
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/receipt_print.xml'
    ],
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
