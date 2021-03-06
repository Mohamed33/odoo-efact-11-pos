# -*- coding: utf-8 -*-
# Copyright 2017, OdooTips

{
    'name': 'Monto en letras - Reporte Facturas',
    'summary': """Este módulo convierte el monto total de una factura
                a texto (En el reporte QWeb)""",
    'version': '11.0',
    'category': 'tools',
    'website': 'https://odootips.com',
    'author': 'OdooTips',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'base_setup',
        'account',
        'efact',
        "sale"
    ],
    'data': [
        'reports/assets.xml',
        'views/res_currency_view.xml',
		'views/report_invoice_document.xml',
        'views/report_saleorder_document.xml',
        'views/header.xml',
        'views/res_company_view.xml'
    ],
}