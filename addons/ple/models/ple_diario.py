from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import codecs

class ple_diario (models.Model):
    _inherit = "ple.base"
    _name="ple.diario"

    linea = fields.One2many('ple.diario_linea', 'base_id', string="detalle de reporte")

    @api.multi
    def imprimir(self):
        self.ensure_one()
        return self.env.ref('ple.report_diario_05_1').report_action(self)

    @api.one
    def recargar(self):
        self.env["ple.diario_linea"].search([("period_id_linea.code", "=", self.period_id.code)]).unlink()

        linea_obj = self.env['ple.diario_linea']
        docs = self.env["account.move.line"].search([("period_id.code", "=", self.period_id.code),("parent_state","!=","draft")])

        for li in self.browse(self.ids):
            for doc in docs:
                linea_obj.create({
                    'base_id': li.id,
                    'cuo': doc.move_id.id,
                    'period_id_linea': doc.period_id.id,
                    'currency_id_name': doc.currency_id.name,
                    'partner_id_code' : doc.partner_id.tipo_documento,
                    'partner_vat' : doc.partner_id.vat,
                    'journal_code_name': doc.journal_id.invoice_type_code_id,
                    'serie': doc.invoice_id.number[:4],
                    'correlativo': doc.invoice_id.number[8:],
                    'date_invoice': doc.date,
                    'date_due': doc.date_maturity,
                    'account_code': doc.account_id.code,
                    'account_name' : doc.account_id.name,
                    'glosa' : doc.name,
                    'debe' : doc.debit,
                    'haber' : doc.credit,

                })
        return True


    @api.multi
    def exportar(self):
        self.write({'state': 'exported'})
        self.sin_movimiento = False
        file_data = self._get_txt()
        # LERRRRRRRRRRRAAAAMM0005010000OIM1.TXT
        file_name = "LE" + self.company_id.partner_id.vat + modificar_fecha_periodo(self.period_id.code)+ "00" + "501000" + "0011" + "1"  + "1.txt"
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
        i = 1
        txt = ""
        documents = self.env['ple.diario'].search([['period_id.code', '=', self.period_id.code]])

        if len(documents) > 1:
            raise UserError("Periodo repetido")

        for document in documents.linea:

            txt += modificar_fecha_periodo(document.period_id_linea.code) + "|" + document.cuo + "|M" + document.cuo + "|"
            # EMPIEZA CAMPO 4
            txt += document.account_code + "|" + "|" + "|"+"|"+ document.partner_id_code + "|" + document.partner_vat + "|"
            # EMPIEZA CAMPO 10
            txt += document.journal_code_name + "|" + document.serie + "|" + document.correlativo + "|"
            # EMPIEZA CAMPO 13
            txt += modificar_fecha(document.date_invoice) + "|" +modificar_fecha(document.date_due) + "|" + modificar_fecha(document.date_invoice) + "|" + document.glosa +"|" +"|"
            # EMPIEZA CAMPO 18
            txt += str(document.debe)  + "|" + "|"+ str(document.haber)+ "|" + "|"+str(document.estado)+ "|"

            txt += "\r\n"
            i += 1

        if i == 1:
            raise UserError("No existen documentos")

        return txt


def modificar_fecha_periodo(fecha):
    if fecha:
        fecha = str(fecha)
        return fecha[3:7] + fecha[0:2] + "00"
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


class ple_diario_linea(models.Model):
    _inherit = 'ple.linea'
    _name = 'ple.diario_linea'

    base_id = fields.Many2one('ple.diario')

    account_code = fields.Char()
    account_name=fields.Char()
    glosa=fields.Char()
    debe = fields.Float()
    haber = fields.Float()


