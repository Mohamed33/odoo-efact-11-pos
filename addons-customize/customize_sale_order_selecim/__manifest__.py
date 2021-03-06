# -*- coding: utf-8 -*-
{
    'name': "Sale Order - Customize Selecim",

    'summary': """
        Personalización de Reporte de impresión de Orden de Venta""",

    'description': """
        Personalización de Reporte de impresión de Orden de Venta
    """,

    'author': "Basic Well",
    'website': "http://www.basicwell.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sunat_get_data'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/external_layout_boxed.xml',
        'reports/sale_order_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}