# -*- coding: utf-8 -*-
{
    'name': "Gestor Concesionario",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "RParedes",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','stock',
                'sale_stock', 'account',
                'odoope_einvoice_base', 'odoope_toponyms',
                'point_of_sale','web',
                'pos_journal_sequence', 'pos_ticket_extend','pos_orders_reprint'
                ],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/pos_concesionario_template.xml',
        'views/pos_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "qweb": [
        'static/src/xml/pos.xml',
    ],
}