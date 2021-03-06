# -*- coding: utf-8 -*-

{
    'name': 'Pos Shortcut Access',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Pos shortcut allows us to access point of sale with keyboard shortcuts.',
    'description': """

=======================

Pos shortcut allows us to access point of sale with keyboard shortcuts.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/keyboard.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 29,
    'currency': 'EUR',
}
