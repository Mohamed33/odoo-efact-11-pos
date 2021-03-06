# -*- coding: utf-8 -*-
{
    'name': "Línea de Crédito del Cliente",

    'summary': """
        Configura la línea de crédito que tiene el cliente en tu empresa. 
        El módulo te alertará de la línea de crédito de tu cliente cuando 
        trates de confirmar una venta o validar una factura.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HIGHLAND TRADING SAC",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','efact','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
        'views/views.xml'
    ],
}