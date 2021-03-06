{
	"name": "Direct Print to Dot Matrix Printer",
	"version": "1.5",
	"depends": [
		
		"purchase",
		"mail",
		"efact"
	],
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"category": "Utilities",
	'website': 'http://www.vitraining.com',
	'images': ['static/description/images/main_screenshot.jpg'],
	'price': '70',
	'currency': 'USD',
	'license':'OPL-1',
	'summary': 'This is modul is used to print PO, Picking, Invoice directly to dot matrix printers',
	"description": """\

Manage
======================================================================

* this is modul is used to print PO, Picking, Invoice, and Picking directly to dot matrix printer
* no special hardware needed
* using printer proxy script (apache/ngnix+php)
* add printer_data field on account.invoice, sale.order, purchase.order, stock.picking
* printer template data from mail.template named "Dot Matrix *"

Installation
======================================================================
* install this addon on the database
* download the print.php script from this <a href="https://drive.google.com/open?id=17aHbikQMjYq7A6AhWoUHsNF4fLomTy4E">link</a> and install it to your local client thats connected to the printer directly.
* install apache+php or nginx+php on the local computer and copy print.php script to the htdocs
* follow the INSTALL.TXT instruction on how to install the script
* print Invoice, SO, PO, Picking directly to local dotmatrix printer

""",
	"data": [
		"view/web_asset.xml",
		"view/invoice.xml",
		"view/po.xml",
		"view/picking.xml",
		"view/so.xml",
		"view/guia_remision.xml",
		"data/templates.xml",
	],
	'qweb': [
		'static/src/xml/web_print_button.xml',
	],
	
	"installable": True,
	"auto_install": False,
    "application": True,
}