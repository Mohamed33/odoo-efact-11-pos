# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Sale Order',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Sales',
    'maintainer': 'Craftsync Technologies',
   
    'summary': """Cancel sales Order app is helpful plugin to cancel processed sale order. Cancellation of sale order includes operations like cancel Invoice, Cancel Delivery Order, Cancel paid Invoice, Unreconcile Payment.""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['sale_management','stock','account_cancel','sale_stock'],
    'data': [
        'views/stock_warehouse.xml',
	    'views/view_sale_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 49.00,
    'currency': 'EUR',

}
