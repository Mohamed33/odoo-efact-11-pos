# -*- coding: utf-8 -*-
{
    'name': "Dashboard Enfocado a Negocios Retail",

    'summary': """
        Este modulo cumple la funcion de automatizar la presentacion de informacion critica para la toma de decisiones para retail""",

    'description': """
    """,

    'author': "Facturacion VIP",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','ks_dashboard_ninja','account','point_of_sale','bi_pos_margin','efact'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'demo/demo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}