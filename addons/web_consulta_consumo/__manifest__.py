{
    'name': "Consulta de Consumo de Comensales",

    'summary': """
       Este módulo permite a los comensales ver un reporte de su consumo diario,semanal y mensual""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Roomies Four",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','gestor_concesionario','sale','point_of_sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'templates/form.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
