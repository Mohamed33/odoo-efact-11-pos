# -*- coding: utf-8 -*-

{
    "name":"Reporte POS de Cierre de Caja",
    "summary":"""
        Genera reporte en PDF de cierre de caja
    """,
    "description":"""
        Genera reporte en PDF de cierre de caja
    """,
    'version': '11.0',
    'category': 'tools',
    'author': 'VICTOR DANIEL MORENO LOPEZ',
    'license': 'AGPL-3',
    'application': False,
    'license': "OPL-1",
    'auto_install': True,
    'installable': True,

    "depends":["base","base_setup","point_of_sale"],
    "data":["views/template.xml","views/report.xml"]
}