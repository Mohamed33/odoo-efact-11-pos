# -*- coding: utf-8 -*-
{
    'name': "ple",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_period','tipocambio'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
       # 'views/sunat_view.xml',
        'views/ventas_view.xml',
        'views/ventas_simplificado_view.xml',
        'report/ple_ventas_14_1.xml',
        'report/ple_ventas_14_2.xml',
        'views/compras_view.xml',
        'views/compras_simplificado_view.xml',
        'report/ple_compras_08_1.xml',
        'views/diario_view.xml',
        'views/account_invoice_form.xml',
        'report/ple_diario_05_1.xml',
        'views/compras_nd_view.xml',
        'security/res_groups.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}