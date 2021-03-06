{
    'name': 'Adaptiv Backend Theme',
    'version': '11.0.1.104',
    'category': 'Themes/Backend',
    'summary': "Enhance your Odoo experience with this completely rewritten backend theme for Odoo 11.",
	'description': "",
    'author': 'Adaptiv Design',
    'license': 'OPL-1',
    'price': 149.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': True,
    'url': 'http://demo.adaptiv.nl',
    'live_test_url': 'http://demo.adaptiv.nl',
    'depends': [
        'web',
        'web_diagram',
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/theme_data.xml',
        'views/webclient_templates.xml',
        'views/theme_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/main.png',
        'static/description/main_screenshot.png'
    ]
}
