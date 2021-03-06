# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Purchase Order',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Purchases',
    'maintainer': 'Craftsync Technologies',
    'description' : 'Cancel PO is used for cancel purchase order and related incoming shipment even if was in done state with that po and also cancel related bill even if it was paid',
    'summary': """Cancel purchases Order app is helpful plugin to cancel processed purchase order. Cancellation of purchase order includes operations like cancel Invoice, Cancel Delivery Order.""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['purchase','account_cancel'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_purchase_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 39.00,
    'currency': 'EUR',  

}
