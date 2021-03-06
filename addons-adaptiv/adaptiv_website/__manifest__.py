{
    'name': 'Adaptiv Website',
    'version': '11.0.1.100',
    'category': 'Hidden',
    'website': 'http://www.adaptiv.nl',
	'summary': "Bridge module between adaptiv_web and website",
    'description': "",
    'author': 'Adaptiv Design',
    'license': '',
    'auto_install': True,
    'depends': [
        'website',
        'adaptiv_portal',
        'adaptiv_web'
    ],
    'data': [
        'views/website_templates.xml',
        'views/website_user_templates.xml'
    ],
}
