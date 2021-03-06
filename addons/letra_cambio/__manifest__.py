# -*- coding: utf-8 -*-
{
    'name': "letra_cambio",

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
    'depends': ['base','account','tipocambio'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/emision_letra_view.xml',
        'views/renovacion_letra_view.xml',
        'views/letra_cambio_view.xml',
        'views/parametros.xml',
        'views/aceptar_letras_view.xml',
        'views/protestar_letras_view.xml',
        'views/aceptar_letra_descontada_view.xml',
        'views/pago_letras_view.xml',
        'views/anular_letras_view.xml',
        'wizard/cambiar_estado_letras_wizard_view.xml',
        'wizard/aceptar_letras_wizard_view.xml',
        'wizard/aceptar_letras_descontada_wizard_view.xml',
        'wizard/estado_pagado_letras_wizard_view.xml',
        'wizard/anular_letras_wizard_view.xml',
        'wizard/protestar_letras_wizard_view.xml',
        'report/letra_cambio_report.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}