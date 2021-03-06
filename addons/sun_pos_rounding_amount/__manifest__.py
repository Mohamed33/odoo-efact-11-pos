{
    'name': 'POS Rounding Amount (Communnity & Enterprise)',
    'version': '11.0.6',
    'summary': 'POS Rounding Amount',
    'price': 18.00,
    'currency': 'EUR',
    'author': 'Kiran Kantesariya',
    'description': "POS Rounding Amount",
    'license': 'OPL-1', 
    'category': 'Point Of Sale',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/sun_pos_rounding_amount.xml',
        'views/point_of_sale.xml',
        'views/pos_config.xml',
    ],
    'images': ['static/description/main_screenshot.jpg'],
    'qweb': [
        'static/src/xml/payment.xml',
        'static/src/xml/receipt.xml'
    ],
    'installable': True,
    'application': True,
}
