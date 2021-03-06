# -*- coding: utf-8 -*-
{
    'name': "Personalización para Grupo RHINN",

    'summary': """
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Daniel Moreno",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','account','efact','bi_picking_move_from_invoice'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_change_product_qty.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}