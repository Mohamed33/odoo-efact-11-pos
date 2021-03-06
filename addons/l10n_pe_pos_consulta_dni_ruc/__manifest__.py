# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Pos consulta de datos dni, ruc',
    'version': '11.0',
    'author': 'Bitodoo',
    'category': 'Point of Sale',
    'summary': 'Pos consulta de datos dni, ruc',
    'website': 'https://www.bitodoo.com',
    'license': 'AGPL-3',
    'description': """
        Pos consulta de datos dni, ruc
    """,
    'depends': ['point_of_sale', 'sunat_get_data'],
    'data': [
        'template/template.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}
