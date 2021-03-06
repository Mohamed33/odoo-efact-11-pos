{
    'name': 'Adaptiv Web Settings Dashboard',
    'version': '11.0.1.100',
    'category': 'Hidden',
    'website': 'http://www.adaptiv.nl',
    'summary': "Removes branding from the settings dashboard",
	'description': "",
    'author': 'Adaptiv Design',
    'license': '',
    'auto_install': True,
    'depends': [
        'adaptiv_web',
        'web_settings_dashboard'
    ],
    'data': [
        'views/webclient_templates.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ]
}
