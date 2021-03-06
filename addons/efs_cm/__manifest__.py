# -*- coding: utf-8 -*-
{
    'name': "EscuelaFullStack Courses Management",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Escuela Full Stack (Victor Cueva)",
    'website': "https://escuelafullstack.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}