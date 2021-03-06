# -*- coding: utf-8 -*-
{
    'name': "Report de Comprobantes de Efact en Excel",

    'summary': """
        Exportación de Comprobantes de Efact en Excel""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Reporte de Comprobantes",
    'website': "http://www.facturacion.vip",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','efact','report_xlsx','account_period'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}