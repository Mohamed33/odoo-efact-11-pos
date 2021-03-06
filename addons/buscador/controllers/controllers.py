# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class buscador(http.Controller):

    @http.route('/consulta', auth='public')
    def index(self, **kwargs):
        return request.render('buscador.form')

    @http.route('/busqueda', type='http', auth='public', method=["POST"], csrf=False)
    def consulta(self, **post):
        correlativo = post.get("correlativo","")
        try:
            correlativo = str(int(correlativo))
        except Exception as e:
            return "El número correlativo es erróneo"

        numero = post.get("serie")+"-"+ correlativo.zfill(8)
        fecha = post.get("fecha")
        ruc = post.get("ruc")
        total = post.get("total")
        documento = request.env["account.invoice"].sudo().search([['move_name',"=",numero],['partner_id.vat',"=",ruc],['date_invoice','=',fecha],['amount_total','=',total]])
        account_invoice_log = False

        if documento.exists():
            if len(documento.account_log_status_ids):
                account_invoice_log = documento.account_log_status_ids[len(documento.account_log_status_ids)-1]
        else:
            return "No se ha encontrado"
            
        identificador = ""
        nombre = ""
        if account_invoice_log:
            identificador = account_invoice_log.api_request_id
            nombre = account_invoice_log.name

        return request.render('buscador.documentos',{'documento' : documento,"identificador":identificador})

    @http.route("/consulta/comprobante/xml/<identificador>",type='http',method=["GET"],csrf=False)
    def comprobante_xml(self,identificador):
        log = request.env["account.log.status"].sudo().search([["api_request_id","=",identificador]])
        xml = log.signed_xml_data
        xml_headers = [
            ('Content-Type', 'application/xml'),
            ('Content-Length', len(xml)),
            ('Content-Disposition', 'attachment; filename="%s.xml"'%(log.name)),
        ]
        return request.make_response(xml, headers=xml_headers)

    @http.route("/consulta/comprobante/pdf/<identificador>",type='http',method=["GET"],csrf=False)
    def comprobante_pdf(self,identificador):
        log = request.env["account.log.status"].sudo().search([["api_request_id","=",identificador]])
        invoice = log.account_invoice_id
        if invoice:
            pdf = request.env.ref('account.account_invoices_without_payment').sudo().render_qweb_pdf([invoice.id])[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), 
                                ('Content-Length', len(pdf)),
                                ('Content-Disposition', 'attachment; filename="%s.pdf"'%(log.name))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/')

    @http.route("/consulta/comprobante/v2/pdf/<compId>",type='http',method=["GET"],csrf=False)
    def comprobante_pdf_v2(self,compId):
        invoice = request.env["account.invoice"].sudo().browse(int(compId))
        
        if invoice:
            invoice = invoice[0]
            pdf = request.env.ref('account.account_invoices_without_payment').sudo().render_qweb_pdf([invoice.id])[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), 
                                ('Content-Length', len(pdf)),
                                ('Content-Disposition', 'attachment; filename="%s.pdf"'%(invoice.move_name))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/')

        #    ['|', ["vat", "=", identificador], ["codigo", "=", identificador], ["es_comensal", "=", True]])

#     @http.route('/json/json/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('json.listing', {
#             'root': '/json/json',
#             'objects': http.request.env['json.json'].search([]),
#         })

#     @http.route('/json/json/objects/<model("json.json"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('json.object', {
#             'object': obj
#         })