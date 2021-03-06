# -*- coding: utf-8 -*-
{
    'name': "Personalización para Grupo Naomi's",

    'summary': """
        Personalización de Flujo de Ventas""",

    'description': """
        Long description of module's purpose
    """,

    'author': "NEX",
    'website': "http://gruponaomis.nex.business",

    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','efact','report_xlsx','vit_dotmatrix','invoice_with_stock_move',
                'sale_combo_product'],

    'data': [
        # 'security/ir.model.access.csv',
        'wizard/sale_supervisor_report_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/guia_remision_masiva.xml',
        'views/guia_remision.xml',
        'views/wizard_reports.xml',
        'views/account_invoice.xml',
        'views/stock_views.xml',
        'views/sale_order.xml',
        'views/product.xml',
        'views/guia_remision_report.xml',
        'views/nota_pedido.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'server/confirmacion_masiva_ventas.xml',
        'security/groups.xml',
        'report/report.xml',
        'report/report_sale_supervisor.xml',
        'template/invoice.xml'
    ],

}