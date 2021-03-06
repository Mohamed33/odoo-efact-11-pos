from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs

class ple_compras (models.Model):
    _inherit= "ple.base"
    _name = "ple.compras_simple"


    linea = fields.One2many('ple.compras_simple_linea', 'base_id' , string="detalle de reporte")

    @api.multi
    def imprimir(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'ple.ple_template_compras_08_1')

    @api.one
    def recargar(self):
        self.env["ple.compras_simple_linea"].search([("period_id_linea.code", "=", self.period_id.code)]).unlink()

        self.write({'state': 'generated'})
        linea_obj = self.env['ple.compras_simple_linea']
        docs = self.env["account.invoice"].search([("period_id", "=", self.period_id.code), ("type","=","in_invoice"),("state","!=","draft")])
        for li in self.browse(self.ids):
            for doc in docs:
                linea_obj.create({
                    'base_id': li.id,
                    'cuo' : doc.move_id.id,
                    'period_id_linea': doc.period_id.id,
                    'date_invoice' : doc.date_invoice,
                    'date_due' : doc.date_due,
                    'journal_code_name' : doc.journal_id.invoice_type_code_id,
                    'serie' : doc.number[:4],
                    'correlativo' : doc.number[8:],
                    'partner_id_code' : doc.partner_id.tipo_documento,
                    'partner_vat' : doc.partner_id.vat,
                    'partner_name' : doc.partner_id.name,
                    'amount_untaxed' : doc.amount_untaxed,
                    'amount_tax' : doc.amount_tax,
                    'amount_total' : doc.amount_total,
                    'currency_id_name': doc.currency_id.name,
                    'tipo_cambio' : doc.tipo_cambio,
                    'refund_invoice_date': doc.refund_invoice_id.date_invoice,
                    'refund_invoice_journal_code': doc.refund_invoice_id.journal_id.invoice_type_code_id,
                    'refund_invoice_serie': get_serie(doc.refund_invoice_id.number),
                    'refund_invoice_correlativo': get_correlativo(doc.refund_invoice_id.number),
                    'num_detraccion' : doc.num_detraccion,
                    'fecha_detraccion' : doc.fecha_detraccion,
                    'estado': doc.estado


                })
        return True

    @api.multi
    def exportar(self):
        self.write({'state': 'exported'})
        self.sin_movimiento = False
        #self.nro_generados = self.nro_generados + 1
        file_data = self._get_txt()
        #LERRRRRRRRRRRAAAAMM0008030000OIM1.TXT
        file_name = "LE" + self.company_id.partner_id.vat +modificar_fecha_periodo(self.period_id.code)+"080300"+"001"+("0" if self.sin_movimiento else "1" )+"1"+"1.txt"
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
        documents = self.env['ple.compras_simple'].search([ ['period_id.code', '=', self.period_id.code] ])

        if len(documents)>1:
            raise UserError("Periodo repetido")

        for document in documents.linea:

            txt += modificar_fecha_periodo(document.period_id_linea.code)+ "|" + document.cuo + "|M"+document.cuo+ "|" + modificar_fecha(document.date_invoice) + "|" + modificar_fecha(document.date_due) + "|" + document.journal_code_name + "|" + document.serie +  "|" + document.correlativo+"|"+"|"
            # EMPIEZA CAMPO 10
            txt += document.partner_id_code + "|" + document.partner_vat + "|" + (document.partner_name if document.partner_id_code == "6" else document.partner_name) + "|"
            # EMPIEZA CAMPO 13
            txt += str(document.amount_untaxed) + "|" + str(document.amount_tax) + "|" + "|" + str(document.amount_total)  + "|"
            # EMPIEZA CAMPO 17
            txt += document.currency_id_name + "|"+str(document.tipo_cambio if document.tipo_cambio else 1.000)+"|"
            # EMPIEZA CAMPO 19
            if document.journal_code_name == "07" or document.journal_code_name == "08":
                txt += "nota"  #modificar_fecha(document.refund_invoice_date)+ "|" + document.refund_invoice_journal_code + "|" + document.refund_invoice_serie + "|" + "|" + document.refund_invoice_correlativo
            else:
                txt += "|" + "|" + "|" + "|"
            # EMPIEZA CAMPO 23
            txt += (modificar_fecha(document.fecha_detraccion) if document.fecha_detraccion else "" )+ "|" + (document.num_detraccion if document.fecha_detraccion else "" ) + "|" + "|" + "|" + "|" + "|" + "|"
            # EMPIEZA CAMPO 30
            txt += "1" +"|"+ str(document.estado) + "|"
            txt += "\r\n"
            i += 1


        if i == 1:
            #raise UserError("Sin movimiento")
            self.sin_movimiento=True

        return txt


def modificar_fecha_periodo(periodo):
    if periodo:
        fecha = str(periodo)
        return periodo[3:7]+periodo[0:2]+"00"
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


class ple_compras_linea(models.Model):
    _inherit = 'ple.linea'
    _name = 'ple.compras_simple_linea'

    base_id = fields.Many2one('ple.compras_simple')
    fecha_detraccion = fields.Date()
    num_detraccion = fields.Char()


class invoice_compra(models.Model):
    _inherit = "account.invoice"

    fecha_detraccion = fields.Date()
    num_detraccion= fields.Char()



