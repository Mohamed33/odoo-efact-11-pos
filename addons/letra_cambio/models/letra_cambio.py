from odoo import fields,models,api
from odoo import exceptions, _
from odoo.exceptions import ValidationError, UserError
import datetime , codecs
from .number_to_letter import to_word

class LetraCambio(models.Model):
    _name = "letra_cambio.letra"

    name = fields.Char(related='number')

    emision_id = fields.Many2one('letra_cambio.emision_letra', string='emision',
                                 ondelete='restrict', index=True, states={'draft': [('readonly', False)]})

    canjeado_id = fields.Many2one('letra_cambio.renovacion_letra', string='canjeado',
                                    ondelete='restrict', index=True, states={'draft': [('readonly', False)]})

    renovacion_id = fields.Many2one('letra_cambio.renovacion_letra', string='renovado',
                                 ondelete='restrict', index=True, states={'draft': [('readonly', False)]})

    number = fields.Char(string='Número', store=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Cliente', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always', related='emision_id.partner_id')
    date_doc = fields.Date(string='Fecha emisión', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    date_due = fields.Date(string='Fecha vencimiento', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    #amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='get_monto_letra')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='always')
    tipo_cambio = fields.Float("T/C", digits=(1, 3))

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})

    cuenta_banco = fields.Many2one('account.account', string='Banco', domain=[('code', 'like', '10%')])

    cuenta_banco_journal = fields.Many2one('account.journal', string='Banco', domain=[('type', '=', 'bank')])

    company_id = fields.Many2one("res.company",required=True,string="Compañia",default=lambda self: self.env.user.company_id.id)

    monto_en_letras = fields.Char(compute="compute_number_to_letter", stirng="Monto en Letras")

    partner_aceptante_id = fields.Many2one("res.partner",required=True,string="Aceptante")

    partner_aval_id = fields.Many2one("res.partner",required=True,string="Aval")

    date_doc_con = fields.Char(compute="convert_date", stirng="Monto en Letras",store="True")
    date_due_con = fields.Char(compute="convert_date", stirng="Monto en Letras",store="True")

    @api.depends('date_doc','date_due')
    def convert_date(self):
        for rec in self:
            rec.date_doc_con = fields.Date.from_string(rec.date_doc).strftime('%d/%m/%Y')
            rec.date_due_con = fields.Date.from_string(rec.date_due).strftime('%d/%m/%Y')
    
    @api.depends('amount_total')
    def compute_number_to_letter(self):
        for record in self:
            record.monto_en_letras = to_word(record.amount_total)
        



    gasto = fields.Monetary(string='gastos', store=True )


    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ACE', 'Aceptada'),
        ('COB', 'Cobranza'),
        ('DES', 'Descuento'),
        ('DEA', 'Desc. Aceptada'),
        ('PRO', 'Protestada'),
        ('ANU', 'Anulada'),
        ('PAG', 'Pagado'),
        ('CJE', 'Canjeado'),
        ('REN', 'Renovado'),
    ], default='draft', string='Estado inicial',readonly=True)

    #state_final = fields.Selection('_compute_selection', string="Estado final" ,store=False)

    state_end = fields.Selection([
        ('draft', 'Borrador'),
        ('ACE', 'Aceptada'),
        ('COB', 'Cobranza'),
        ('DES', 'Descuento'),
        ('DEA', 'Desc. Aceptada'),
        ('PRO', 'Protestada'),
        ('ANU', 'Anulada'),
        ('PAG', 'Pagado'),
        ('CJE', 'Canjeado'),
        ('REN', 'Renovado'),
    ], string='Estado final')

    def get_monto_letra(self):
        self.amount_total= self.emision_id.monto_emitir / self.emision_id.cantidad_letras


    def set_date_due2(self,day):
        #self.date_due = self.date_doc + datetime.timedelta(days=7)
        self.date_due = (datetime.datetime.strptime(self.date_doc, '%Y-%m-%d') + datetime.timedelta(
            days=day)).strftime('%Y-%m-%d')


    def set_date_due(self, day):
        # self.date_due = self.date_doc + datetime.timedelta(days=7)
        return (datetime.datetime.strptime(self.date_doc, '%Y-%m-%d') + datetime.timedelta(
            days=day)).strftime('%Y-%m-%d')

    def set_date_due3(self):
        #self.date_due = self.date_doc + datetime.timedelta(days=7)
        self.date_due = (datetime.datetime.strptime(self.date_doc, '%Y-%m-%d') + datetime.timedelta(
            days=7)).strftime('%Y-%m-%d')

#        @api.multi
#        def _compute_selection(self):
#            if True:
#                selection_options = [('e', 'Email'), ('p', 'phone'), ('m', 'Post/Mail')]
#            else:
#                selection_options = [('a', 'Automatic Action')]
#            return selection_options


    def cambio_estado(self):
        conf = self.env['ir.config_parameter']
        gastos =False

        if not self.state_end :
            raise UserError("Seleccione un estado")

        if self.state_end in ['DES','DEA','PAG'] and not self.cuenta_banco:
            raise UserError("Defina una cuenta Bancaria")

        if self.state == 'draft' and  self.state_end == 'ACE':
            cuenta1 = self.env['account.account'].search([("code", "=",str(conf.get_param('letra_aceptada')) )]) #en cartera DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #cuenta por cobrar  HABER
            name = "Por la letra Aceptada/Cartera"

        elif self.state == 'ACE' and self.state_end == 'COB':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_cobranza')) )]) #en cobranza  DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Cartera a Cobranza"

        elif self.state == 'COB' and self.state_end == 'ACE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera  DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_cobranza')) )]) #en cobranza HABER
            name = "Por la letra de Cobranza a Cartera"

        elif self.state == 'DES' and self.state_end == 'ACE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descuento')) )]) #en descuento HABER
            name = "Por la letra en Descuento a Cartera"

        elif self.state == 'ACE' and self.state_end == 'PRO':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_protestada')) )]) #en protestada DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gasto_protestada')))])  # gastos DEBE
            cuenta3 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Cartera a Protestada"
            gastos = True

        elif self.state == 'COB' and self.state_end == 'PRO':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_protestada')) )]) #en protestada DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gasto_protestada')))])  # gastos DEBE
            cuenta3 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_cobranza')) )]) #en protestada HABER
            name = "Por la letra en Cobranza a Protestada"
            gastos = True

        elif self.state == 'PRO' and self.state_end == 'ACE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_protestada')) )]) #protestada HABER
            name = "Por la letra Protestada a Cartera"


        elif self.state == 'ACE' and self.state_end == 'DES':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descuento')) )]) #en descuento DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Cartera a Descuento"

        elif self.state == 'DES' and self.state_end == 'DEA':
            cuenta1 = self.cuenta_banco  # cuenta banco  # cobro adelantado DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gasto_descontada_aceptada')))])  # gastos DEBE
            cuenta3 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descontada_aceptada')) )]) #letra descotada aceptada (deuda con el banco) HABER
            name = "Por la aceptacion de la letra descontada"
            gastos=True

        elif self.state == 'DEA' and self.state_end == 'PAG':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descontada_aceptada')) )]) #descontada aceptada (deuda bancaria) dbee
            #cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gastos_financieros')))])  # gastos DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descuento')))])  # descontada que quedo pendient HABER
            name = "Por la letra decontada aceptada a Pagada"


        elif self.state == 'DEA' and self.state_end == 'PRO':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descontada_aceptada')) )]) #descontado DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gasto_protestada')))])  # gastos DEBE
            cuenta3 = self.cuenta_banco  # cuenta banco devolucion  # HABER
            name = "Por la letra en Descuento a Protestada"
            gastos = True

        elif self.state == 'ACE' and self.state_end == 'PAG':
            cuenta1 = self.cuenta_banco # cuenta banco DEBE
            #cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gastos_financieros')))])  # gastos DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Cartera a Pagada"

        elif self.state == 'COB' and self.state_end == 'PAG':
            cuenta1 = self.cuenta_banco # cuenta banco DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('gasto_cobranza_libre')))]) # gastos DEBE
            cuenta3 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_cobranza')) )]) #en cartera HABER
            name = "Por la letra en Cobranza a Pagada"
            gastos = True

        elif self.state == 'PRO' and self.state_end == 'PAG':
            cuenta1 = self.cuenta_banco # cuenta banco DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_protestada')) )]) #en cartera HABER
            name = "Por la letra en Protestada a Pagada"

        elif self.state == 'draft' and self.state_end == 'ANU':
            self.state = self.state_end
            self.state_end = ""
            return

        #casos de letras en canje y renovacion

        elif self.state == 'ACE' and self.state_end == 'CJE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #por cobrar DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Cartera a Canjeada"

        elif self.state == 'COB' and self.state_end == 'CJE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #canjeada DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_cobranza')) )]) #en cartera HABER
            name = "Por la letra en Cobranza a Canjeada"

        elif self.state == 'DEA' and self.state_end == 'CJE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #canjeada DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_descontada_aceptada')) )]) #en cartera HABER
            name = "Por la letra en Descuento a Canjeada"

        elif self.state == 'PRO' and self.state_end == 'CJE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #canjeada DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_protestada')) )]) #en cartera HABER
            name = "Por la letra Protestada a Canjeada"

        elif self.state == 'REN' and  self.state_end == 'ACE':
            cuenta1 = self.env['account.account'].search([("code", "=", str(conf.get_param('letra_aceptada')) )]) #en cartera DEBE
            cuenta2 = self.env['account.account'].search([("code", "=", str(conf.get_param('cuenta_por_cobrar')) )]) #cuenta por cobrar  HABER
            name = "Por la letra Renovada a Aceptada/Cartera"

        else : raise UserError("Utilice un estado aceptable")

        if not gastos :

            line=[(0, 0, {
                "account_id": cuenta1.id,
                "partner_id": self.partner_id.id,
                "name": name,
                'amount_currency' : self.amount_total,
                'currency_id': self.currency_id.id,
                "debit": self.amount_total*self.tipo_cambio ,
                "credit": 0.0,
            }), (0, 1, {
                "account_id": cuenta2.id,
                "partner_id": self.partner_id.id,
                "name": name,
                'amount_currency': -self.amount_total,
                'currency_id': self.currency_id.id,
                "debit": 0.0,
                "credit": self.amount_total*self.tipo_cambio,
            })]

        else:
            line = [(0, 0, {
                "account_id": cuenta1.id,
                "partner_id": self.partner_id.id,
                "name": name,
                'amount_currency': self.amount_total - self.gasto,
                'currency_id': self.currency_id.id,
                "debit": self.amount_total * self.tipo_cambio - self.gasto* self.tipo_cambio,
                "credit": 0.0,
            }), (0, 0, {
                "account_id": cuenta2.id,
                "partner_id": self.partner_id.id,
                "name": name,
                'amount_currency': self.gasto,
                'currency_id': self.currency_id.id,
                "debit": self.gasto*self.tipo_cambio,
                "credit": 0.0,
            }),(0, 0, {
                "account_id": cuenta3.id,
                "partner_id": self.partner_id.id,
                "name": name,
                'amount_currency': -self.amount_total,
                'currency_id': self.currency_id.id,
                "debit": 0.0,
                "credit": self.amount_total * self.tipo_cambio,
            })
                    ]


        asiento = self.env['account.move']
        asiento = asiento.create({
            'ref': self.number,
            'line_ids': line,
            'journal_id': self.journal_id.id,
            'currency_id' : self.currency_id.id,
            'date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'narration': "Asiento de letras",

        })

        self.state= self.state_end
        self.state_end=""
        asiento.post()

    @api.multi
    def cambiar_estado_all(self, values, state):
        for record in values:
            record.state_end = state
            record.cambio_estado()

    @api.multi
    def cambiar_estado_all_gastos(self, values, state,gasto):
        for record in values:
            record.state_end = state
            record.gasto = gasto
            record.cambio_estado()




