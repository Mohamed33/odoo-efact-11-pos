# -*- coding: utf-8 -*-
{
    'name': "Facturación Electrónica Multi-Series",

    'summary': """
        Point Of Sale, Journal""",

    'description': """
        Agregra Diarios y secuencias al punto de venta
    """,

    'author': "Facturacion VIP",
    'website': "https://www.facturacion.vip",

    
    "category": "Point Of Sale",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'efact','point_of_sale','l10n_pe_pos_consulta_dni_ruc'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_config_view.xml',
        'views/pos_journal_sequence_template.xml',
        'views/pos_order.xml'
    ],
    "qweb": [
        'static/src/xml/pos.xml',
    ],
}