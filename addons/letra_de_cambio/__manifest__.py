# -*- coding: utf-8 -*-
{
    'name': "Letra de Cambio",

    'summary': """
        Gestiona las fecha de vencimiento de las letras de cambio por cobrar y por pagar de una factura""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HIGHLAND TRADING COMPANY SAC",
    'website': "http://www.genkopos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',"account"],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'security/res.groups.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}