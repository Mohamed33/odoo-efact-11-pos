from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs

class ple_base (models.AbstractModel):
    _name = "ple.base"
    company_id = fields.Many2one('res.company', string='Company')
    period_id = fields.Many2one('account.period', 'Periodo')
    #journal_id = fields.many2one('account.journal', 'Journal', domain="[('company_id','=',company_id)]", readonly=True,states={'draft': [('readonly', False)], })
    #oportunity_code = fields.selection(_get_oportunity_selection, string="Oportunity Code", required=True)
    #operation_code = fields.selection(_get_operation_selection, string="Operation Code", required=True),
    sin_movimiento = fields.Boolean()
    state = fields.Selection(selection=[
        ('draft', 'Borrador'),
        ('generated', 'Generado'),
        ('exported', 'Exportado'),
    ],default='draft')

    #linea = fields.One2many('ple.linea', 'base_id' , string="detalle de reporte")

    @api.multi
    def imprimir(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'ple.ple_template_ventas_14_1')

    @api.one
    def recargar(self):
        linea_obj = self.env['ple.linea']
        docs = self.env["account.invoice"].search([("state","!=","draft")])
        for li in self.browse(self.ids):
            for doc in docs:
                linea_obj.create({
                    'base_id': li.id,
                    'cuo' : doc.move_id.id,
                    'period_id_linea' : doc.period_id,
                    'date_invoice' : doc.date_invoice,
                    'date_due' : doc.date_due,
                    'journal_code_name' : doc.journal_id.invoice_type_code_id,
                    'serie' : doc.number[:4],
                    'correlativo' : doc.number[8:],
                    'partner_id_code' : doc.partner_id.tipo_documento,
                    'partner_vat' : doc.partner_id.vat,
                    'partner_name' : doc.partner_id.name,
                    'total_venta_gravado':doc.total_venta_gravado,
                    'total_descuento_global':doc.total_descuento_global,
                    'total_tax_discount':doc.total_tax_discount,
                    'total_venta_exonerada':doc.total_venta_exonerada,
                    'total_venta_inafecto':doc.total_venta_inafecto,
                    'amount_untaxed' : doc.amount_untaxed,
                    'amount_tax' : doc.amount_tax,
                    'amount_total' : doc.amount_total,
                    'currency_id_name': doc.currency_id.name,
                    'tipo_cambio_fecha_factura' : doc.tipo_cambio_fecha_factura,
                    'refund_invoice_date': doc.refund_invoice_id.date_invoice,
                    'refund_invoice_journal_code': doc.refund_invoice_id.journal_id.invoice_type_code_id,
                    'refund_invoice_serie': get_serie(doc.refund_invoice_id.number),
                    'refund_invoice_correlativo': get_correlativo(doc.refund_invoice_id.number),
                })
        return True







    @api.multi
    def exportar(self):
        self.write({'state': 'exported'})
        self.sin_movimiento = False
        #self.nro_generados = self.nro_generados + 1
        file_data = self._get_txt()
        file_name = "LE" + self.company_id.partner_id.vat +modificar_fecha_periodo(self.period_id.code)+"1.txt"
        values = {
            'name': file_name,
            'datas_fname': file_name,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas' : codecs.encode(codecs.encode(file_data,'utf8'),'base64'),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    @api.multi
    def _get_txt(self):
        i=1
        txt=""
        documents = self.env['ple.base'].search([ ['period_id.code', '=', self.period_id.code] ])

        if len(documents)>1:
            raise UserError("Periodo repetido")

        for document in documents.linea:

            txt += modificar_fecha_periodo(documents.period_id.code)+ "|" + document.cuo + "|M"+document.cuo+ "|" + modificar_fecha(document.date_invoice) + "|" + modificar_fecha(document.date_due) + "|" + document.journal_code_name + "|" + document.serie + "|" + document.correlativo+"|"+"|"
            txt += document.partner_id_code + "|" + document.partner_vat + "|" + (document.partner_name if document.partner_id_code == "6" else document.partner_name) + "|" + "|"
            txt += str(document.total_venta_gravado) + "|" + str(document.total_descuento_global) + "|" + str(document.amount_tax) + "|" + str(document.total_tax_discount) + "|" + str(document.total_venta_exonerada) + "|" + str(document.total_venta_inafecto) + "|" + "|" + "|" + "|" + "|"
            txt += str(document.amount_total)  + "|" + document.currency_id_name   + "|" + "|"+str(round(document.tipo_cambio_fecha_factura,3))+"|"
            if document.journal_code_name == "07" or document.journal_code_name == "08":
                txt += "nota" + "|" #modificar_fecha(document.refund_invoice_date)+ "|" + document.refund_invoice_journal_code + "|" + document.refund_invoice_serie + "|" + document.refund_invoice_correlativo + "|" + "|" + "|" + "|1|"
            else:
                txt += "|" + "|" + "|" + "|" + "|" + "|" + document.estado
            txt += "\r\n"
            i += 1


        if i == 1:
            # raise UserError("Sin movimiento")
            self.sin_movimiento = True

        return txt

def modificar_fecha_periodo(fecha):
    if fecha:
        fecha = str(fecha)
        return fecha[3:7]+fecha[0:2]+"00"
    else:
        return ""

def modificar_fecha(fecha):
        if fecha:
            fecha = str(fecha)
            return fecha[8:10] + "/" + fecha[5:7] + "/" + fecha[0:4]
        else:
            return ""

def get_serie(number):
    if number:
        return number[0:4]
    else:
        return ""

def get_correlativo(number):
    if number:
        return number[8:]
    else:
        return ""



class ple_linea(models.AbstractModel):
    _name = 'ple.linea'

  # base_id = fields.Many2one('ple.base')
    period_id_linea = fields.Many2one('account.period', 'Periodo')
    cuo = fields.Char('cuo')

    date_invoice = fields.Date(string='Fecha Emision')
    date_due = fields.Date(string='Fecha Vencimiento')
    journal_code_name=fields.Char()
    serie = fields.Char(string='serie')
    correlativo =fields.Char()
    partner_id_code =fields.Char('Tipo doc.')
    partner_vat = fields.Char()
    partner_name =fields.Char()

    total_venta_gravado =fields.Float()
    total_descuento_global =fields.Float()
    total_tax_discount =fields.Float()
    total_venta_exonerada =fields.Float()
    total_venta_inafecto =fields.Float()

    amount_untaxed= fields.Float(string='Base')
    amount_tax= fields.Float(string='IGV')
    amount_total=fields.Float(string='Total')

    currency_id_name =fields.Char()
    tipo_cambio= fields.Float(digits=(1, 3))

    refund_invoice_date =fields.Date()
    refund_invoice_journal_code =fields.Char()
    refund_invoice_serie =fields.Char()
    refund_invoice_correlativo =fields.Char()


    estado = fields.Char()




#    period_id= fields.many2one('account.period', 'Period', required=True, select=1)
#    move_line_id= fields.Many2one('account.move.line', 'Accounting movement', select=1)
#    account_id= fields.Many2one('account.account', 'Account', domain="[('company_id','=',company_id)])")
