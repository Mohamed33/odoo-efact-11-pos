# -*- coding: utf-8 -*-
{
    'name': "POS Ticket",

    'summary': """
        Point Of Sale, Ticket""",

    'description': """
        Point Of Sale Partner details on the ticket
    """,

    'author': "KND",
    'website': "https://www.knd.com",

    'category': 'Point Of Sale',
    'version': '0.1',

    'depends': ['base','point_of_sale','pos_journal_sequence'],

    'data': [
        'views/pos_ticket_template.xml',
    ],
    "qweb": [
        'static/src/xml/pos.xml',
    ],
}