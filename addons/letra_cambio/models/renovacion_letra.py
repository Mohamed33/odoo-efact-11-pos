from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs

class Renovacion_letra_cambio (models.Model):
    _inherit = "letra_cambio.emision_letra"
    _name = "letra_cambio.renovacion_letra"

    letra_anterior_line_ids = fields.One2many('letra_cambio.letra', 'canjeado_id', string='letra por canjear',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True )

    letra_line_ids = fields.One2many('letra_cambio.letra', 'renovacion_id', string='letras renovadas',
                                     readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    @api.onchange('partner_id')
    def add_letras_anterior(self):
        docs = self.env["letra_cambio.letra"].search([("&"),("partner_id.id","=",self.partner_id.id),("|"),("state", "=", "ACE"),("|"),("state", "=", "COB"),("|"),("state", "=", "DES"),("state", "=", "PRO")])
        self.letra_anterior_line_ids =docs

    @api.onchange('currency_id','tipo_cambio','invoice_line_ids','letra_anterior_line_ids')
    def set_monto_emitir(self):
        montodocs=0
        docs = self.invoice_line_ids
        for doc in docs:
            montodocs += doc.residual_company_signed

        montoletra=0

        letras = self.letra_anterior_line_ids
        for let in letras:
            if let.currency_id.name== 'PEN':
                montoletra += let.amount_total

            if let.currency_id.name== 'USD':
                montoletra += let.amount_total*self.tipo_cambio# para llevarlo a soles

        self.monto_emitir = montodocs/self.tipo_cambio + montoletra/self.tipo_cambio

    @api.one
    def set_letras(self):
        letra = self.env['letra_cambio.letra']
        monto_letra = self.monto_emitir / self.cantidad_letras
        monto_letra = self.truncate(monto_letra, 1)

        for li in self.browse(self.ids):
            for i in range(self.cantidad_letras - 1):

                letra.create({
                    'renovacion_id': li.id,
                    'number': str(self.number) + "-" + str(i + 1),
                    'journal_id': self.journal_id.id,
                    'date_doc': self.date_doc,
                    'currency_id': self.currency_id.id,
                    'tipo_cambio': self.tipo_cambio,
                    'amount_total': monto_letra,
                    'state' : 'REN'
                })

            i = self.cantidad_letras - 1

            letra.create({
                'renovacion_id': li.id,
                'number': str(self.number) + "-" + str(i + 1),
                'journal_id': self.journal_id.id,
                'date_doc': self.date_doc,
                'currency_id': self.currency_id.id,
                'tipo_cambio': self.tipo_cambio,
                'amount_total': self.monto_emitir - monto_letra * (self.cantidad_letras - 1),
                'state': 'REN'
            })

        # self.set_date_due()

        return True

    def crear_letras(self):
        self.set_letras()
        self.set_date_due()
        self.write({'state': 'emitido'})
        self.env['letra_cambio.letra'].cambiar_estado_all(self.letra_anterior_line_ids, "CJE")