# -*- coding: utf-8 -*-
{
    'name': "Consulta RUC y DNI",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Facturacion VIP",
    'website': "http://www.facturacion.vip",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','account','odoope_einvoice_base','odoope_toponyms'],
    'external_dependencies':{"python":[]},
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'data/res_company.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}