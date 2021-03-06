# -*- coding: utf-8 -*-
{
    'name': "oimadmin",
    'summary': """OimServer Admin Module""",
    'description': """
        This module manage server of Oim Project.
    """,
    'author': "Highland TC",
    'website': "http://erp.highlandtc.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/oimmenu.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}