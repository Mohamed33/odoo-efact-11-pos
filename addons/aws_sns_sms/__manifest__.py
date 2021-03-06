# -*- coding: utf-8 -*-
{
    'name': "aws_sns_sms",
    'summary': """Envios de sms con AWS-SNS.""",
    'description': """
    Este Modulo ehabilita el envio de sms usando AWS-SNS.
    """,
    'author': "Victor Cueva <ingvcueva@gmail.com>",
    'website': "https://victoralin10.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}