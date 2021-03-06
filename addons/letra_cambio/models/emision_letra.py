from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs
import math

class letra_cambio (models.Model):
    _name = "letra_cambio.emision_letra"

    name =  fields.Char(related= 'number')
    invoice_line_ids = fields.One2many('account.invoice', 'invoice_id', string='Invoice Lines',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True )
    letra_line_ids = fields.One2many('letra_cambio.letra', 'emision_id', string='letra Lines',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    partner_id = fields.Many2one('res.partner', string='Cliente', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')
    payment_term_id = fields.Many2one('account.payment.term', string='Términos de pago',required=True,
                                      readonly=True, states={'draft': [('readonly', False)]})
    number = fields.Char(string='Número', store=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Diario',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_doc = fields.Date(string='Fecha emision ',default=fields.Date.today, readonly=True, states={'draft': [('readonly', False)]}, index=True)
    cantidad_letras = fields.Integer(store=True, states={'draft': [('readonly', False)]})
    monto_emitir = fields.Monetary(string='Total', readonly=True , states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='always' , default=lambda self: self.env.user.company_id.currency_id)
    tipo_cambio = fields.Float("T/C", digits=(1, 3), readonly=True ,states={'draft': [('readonly', False)]})


    comment = fields.Text('Comentarios', states={'draft': [('readonly', False)]})


    state = fields.Selection([
        ('draft', 'Borrador'),
        ('emitido', 'Emitido'),
    ], default='draft',string='Estado')

    @api.onchange('partner_id')
    def add_invoice(self):
        docs = self.env["account.invoice"].search([("state", "=", "open"),("partner_id.id","=",self.partner_id.id)])
        self.invoice_line_ids =docs

    @api.onchange('date_doc')
    def set_journal(self):
        journal =self.env["account.journal"].search([("name", "=", "Letras")])
        self.journal_id= journal.id


    @api.onchange('journal_id')
    def set_code_journal(self):
        self.number = str(self.journal_id.code) + str(self.journal_id.sequence_number_next)

    @api.onchange('currency_id','tipo_cambio','invoice_line_ids')
    def set_monto_emitir(self):
        monto=0
        docs = self.invoice_line_ids
        for doc in docs:
            monto += doc.residual_company_signed

        self.monto_emitir = monto/self.tipo_cambio

    def findMod(self,a, b):

            # Finding mod by repeated subtraction
        mod = a
        while (mod >= b):
            mod = mod - b

        return mod

    def truncate(self , x, d):
        return int(x * (10.0 ** d)) / (10.0 ** d)

    @api.one
    def set_letras(self):
        letra = self.env['letra_cambio.letra']
        monto_letra = self.monto_emitir /self.cantidad_letras
        monto_letra= self.truncate(monto_letra,1)

        for li in self.browse(self.ids):
            for i in range(self.cantidad_letras-1):
                letra.create({
                    'emision_id' : li.id,
                    'number' : str(self.number)+"-"+str(i+1),
                    'journal_id' : self.journal_id.id,
                    'date_doc' : self.date_doc,
                    'currency_id' : self.currency_id.id,
                    'tipo_cambio': self.tipo_cambio,
                    'amount_total' : monto_letra,
                })

            i = self.cantidad_letras-1

            letra.create({
                'emision_id': li.id,
                'number': str(self.number) + "-" + str(i + 1),
                'journal_id': self.journal_id.id,
                'date_doc': self.date_doc,
                'currency_id': self.currency_id.id,
                'tipo_cambio' : self.tipo_cambio,
                'amount_total': self.monto_emitir - monto_letra*(self.cantidad_letras -1),
            })

        #self.set_date_due()
        return True

    @api.onchange('payment_term_id')
    def set_cantidad_letras(self):
        if(self.payment_term_id):
            self.cantidad_letras = len(self.payment_term_id.line_ids)

    def set_date_due(self):
        fila=0
        for letra in self.letra_line_ids:
            payment=self.payment_term_id.line_ids[fila]
            letra.set_date_due2(payment.days)
            fila+=1

    def crear_letras(self):
        self.set_letras()
        self.set_date_due()
        self.write({'state': 'emitido'})

    @api.constrains('tipo_cambio')
    def _check_tipo_cambio(self):
        for record in self:
            if record.tipo_cambio <= 0:
                raise ValidationError("Valor del tipo de Cambio incorrecto")

    @api.onchange('date_doc','currency_id')
    def get_ratio(self):
        if self.date_doc:
            rate = self.env['res.currency.rate'].search([('fecha', "=", self.date_doc),('currency_id',"=",self.currency_id.name)])
            if rate.exists():
                self.tipo_cambio = rate[0].cambio_compra
            elif self.currency_id.name=='PEN':
                self.tipo_cambio = 1.0
            else:
                self.tipo_cambio = 0.0


class AccountInvoice(models.Model):
        _inherit = "account.invoice"

        invoice_id = fields.Many2one('letra_cambio.emision_letra', string='Documentos',index=True)