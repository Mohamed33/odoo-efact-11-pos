# -*- coding: utf-8 -*-

{
    'name': 'Culqi Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: Culqi Implementation',
    'version': '1.0',
    'description': """Culqi Payment Acquirer""",
    'depends': ['payment','account_payment','website_sale','account_invoicing'],
    'author': "Rpareds",
    'website': "http://www.yourcompany.com",
    'data': [
        'views/payment_views.xml',
        'views/payment_culqi_templates.xml',
        'views/account_config_settings_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'external_dependencies': {
        'python': ['culqipy']
    },
    'installable': True,
}
