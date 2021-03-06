# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Product Switch View | POS Switch Product View',
    'version' : '1.0',
    'category': 'Point of Sale',
    'sequence': 1,
    'author' : 'GYB IT SOLUTIONS',
    'website': 'http://www.gybitsolutions.com',
    'license': 'AGPL-3',
    'description': 'List/Form view of products in POS Screen',
    'summary': """User can see product in list view or form view in POS Screen and it's default view is configurable from pos config.""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config.xml',
        'views/point_of_sale.xml',
     ],
    'images': ['static/description/icon.png'],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'price': 10.0,
    'currency': 'EUR',
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
