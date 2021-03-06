# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    'name' : 'Sales Order Filters',
    'author' : 'Softhealer Technologies',
    'website': 'http://www.softhealer.com',
    'category': 'Sales',
    'description': """This module useful to filter sale order by today, yesterday, current week,
    previous week, current month, previous month, current year, previous year.
    """,    
    'version':'11.0.1',
    'depends' : ['base','sale','sale_management'],
    'application' : True,
    'data' : ['views/sale_order_view.xml',
            ],            
    'images': ['static/description/background.png',],              
    'auto_install':False,
    'installable' : True,
    'license': 'LGPL-3',
    "price": 8,
    "currency": "EUR"   
}
