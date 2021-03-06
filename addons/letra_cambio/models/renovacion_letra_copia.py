from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs

class Renovacion_letra_cambio (models.Model):
    _name = "letra_cambio.renovacion_letra"

    letra_anterior_line_ids = fields.One2many('letra_cambio.letra', 'renovacion_id', string='letra anterior',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True )
    letra_renovada_line_ids = fields.One2many('letra_cambio.letra', 'renovacion_id', string='letra renovada',
                                       readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    letra_id = fields.Many2one('letra_cambio.emision_letra', string='Documentos',
                                 ondelete='cascade', index=True)

    partner_id = fields.Many2one('res.partner', string='Cliente', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')
    payment_term_id = fields.Many2one('account.payment.term', string='Términos de pago',required=True,
                                      readonly=True, states={'draft': [('readonly', False)]})
    number = fields.Char(string='Número', store=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Diario'
                                                           '',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_doc = fields.Date(string='Fecha emision ',default=fields.Date.today, readonly=True, states={'draft': [('readonly', False)]}, index=True)
    cantidad_letras = fields.Integer(store=True)
    monto_emitir = fields.Float()
    comment = fields.Text('Comentarios', readonly=True, states={'draft': [('readonly', False)]})


    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], default='draft',string='Estado')

    @api.onchange('partner_id')
    def add_letras_anterior(self):
        docs = self.env["letra_cambio.letra"].search([("&"),("partner_id.id","=",self.partner_id.id),("|"),("state", "=", "ACE"),("|"),("state", "=", "COB"),("|"),("state", "=", "DES"),("state", "=", "PRO")])
        self.letra_anterior_line_ids =docs

    @api.onchange('date_doc')
    def set_journal(self):
        journal =self.env["account.journal"].search([("name", "=", "Letras")])
        self.journal_id= journal.id

    @api.onchange('journal_id')
    def set_code_journal(self):
        self.number = str(self.journal_id.code) + str(self.journal_id.sequence_number_next)

    @api.onchange('letra_anterior_line_ids')
    def set_monto_emitir(self):
        monto=0
        docs = self.letra_anterior_line_ids
        for doc in docs:
            monto += doc.amount_total

        self.monto_emitir = monto

    @api.one
    def set_letras(self):
        letra = self.env['letra_cambio.letra']

        for li in self.browse(self.ids):
            for i in range(self.cantidad_letras):
                letra.create({
                    'renovacion_id' : li.id,
                    'number' : str(self.number)+"-"+str(i+1),
                    'journal_id' : self.journal_id.id,
                    'date_doc' : self.date_doc,
                    'amount_total' : self.monto_emitir/self.cantidad_letras,
                })
        return True

    @api.onchange('payment_term_id')
    def set_cantidad_letras(self):
        if(self.payment_term_id):
            self.cantidad_letras = len(self.payment_term_id.line_ids)

    def set_date_due(self):
        fila=0
        for letra in self.letra_renovada_line_ids:
            payment=self.payment_term_id.line_ids[fila]
            letra.set_date_due2(payment.days)
            fila+=1

