from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from datetime import datetime,timedelta
from ..auth.oauth import enviar_doc_resumen_url,enviar_doc_baja_url,generate_token_by_company,extaer_estado_emision,extraer_error
import json
import requests
import os

class AccountComunicacionBaja(models.Model):
    _name = "efact.account_comunicacion_baja"
    _description = "Documento de baja"

    date_invoice = fields.Date(string='Fecha de Referencia de Comprobante',
                               readonly=True, states={'B': [('readonly', False)]}, index=True,
                               help="Fecha de Referencia de Comprobante", required=True, 
                               copy=False, 
                               default=datetime.now())

 
    issue_date = fields.Date(string='Fecha de Generación de la Comunicación de Baja',
                               help="Fecha de Generación de la Comunicación de Baja", required=True, 
                               copy=False, 
                               default=datetime.now())
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            issue_date = datetime.strptime(self.issue_date, "%Y-%m-%d").strftime("%Y%m%d")
            name = 'RA-' + issue_date +"-"+str(record.contador)
            result.append((record.id, name))
        return result
    
    @api.constrains("date_invoice")
    def _validar_fecha(self):
       # if (datetime.datetime.now()-datetime.datetime.strptime(self.date_invoice, "%Y-%m-%d")).days > 7:
       #print str(datetime.datetime.now())+" || "+ str(datetime.datetime.strptime(self.date_invoice, "%Y-%m-%d"))
       if((datetime.now() - timedelta(7)>datetime.strptime(self.date_invoice, "%Y-%m-%d")) or datetime.strptime(self.date_invoice, "%Y-%m-%d")>datetime.now()):
            raise ValidationError("No se puede enviar documentos con mas de 7 dias de antiguedad")
    """
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('enviado', 'Enviado'),
        ('aceptado_sunat', 'Aceptado Por SUNAT'),
        ('rechazado_sunat', 'Rechazado por SUNAT'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    """
    sent = fields.Boolean(readonly=True, default=False, copy=False,
                          help="It indicates that the invoice has been sent.")

    @api.model
    def _default_documents(self):
        if self._context.get('default_documents', False):
            return self.env['account.invoice'].browse(self._context.get('default_documents'))

    #documents = fields.Many2one('account.invoice', string='Documentos de Baja'
    #                            , readonly=True, states={'draft': [('readonly', False)]}, required=True, default=_default_documents
    #                            )

    #document_line_ids = fields.One2many('facturactiva.baja_documento.line', 'baja_documento_id', string='Documentos de baja',readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'B': [('readonly', False)]}, required=True,
                              default=lambda self: self.env.user)

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'B': [('readonly', False)]})

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)

    #status_envio = fields.Boolean("Estado del envio del documento", default=False)

    json_comprobante = fields.Text(string="JSON de envio")
    
    json_respuesta = fields.Text(string="JSON de respuesta")

    json_estado_comunicacion_baja = fields.Text(string="JSON estado de Comunicación de Baja")

    descripcion_estado_com_baja = fields.Text(string="Descripción de estado de Comunicación de Baja")

    ticket = fields.Char(string ="Ticket")

    state = fields.Selection([
        ('B', 'Borrador'),
        ('E', 'Enviado a SUNAT'),#La comunicación de Baja fue enviada satisfactoriamente. Sin embargo, se tiene que consultar si fue aceptada o rechazada haciendo uso de del ticket.
        ('A', 'Aceptado'),
        ('N', 'Envio Erróneo'),#Rechazado por SUNAT cuando se realiza el envío de la comunicación de baja esto puede ser debido a que sunat esta no disponible o el xml tiene fallos
        ('O', 'Aceptado con Observación'),
        ('R', 'Rechazado'),#Rechazado por SUNAT cuando se consulta con el ticket
        ('P', 'Pendiente de envío a SUNAT'),#SUNAt esta en estado no disponible y su estado pasa a pendiente de envío para enviarse después
        ('C', 'Cancelado')
    ], string="Estado Emision a SUNAT", readonly=True,default='B',copy=False,index=True)

    @api.one
    def default_contador(self):
        cont = 1
        n = 0
        documets = self.env['efact.account_comunicacion_baja'].search_read(
            [['state', '=', 'E'], ['date_invoice', '=', self.date_invoice]],{
                'order':'DESC contador'
            })
        return documets[0].contador + 1

    contador = fields.Integer(string="Contador", states={'B': [('readonly', False)]}, default=default_contador)

    motivo = fields.Text(string="Motivo de Baja", readonly=True, states={'B': [('readonly', False)]}, required=True)

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'B': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('efact.account_comunicacion_baja'))

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if self.search([('id', '!=', invoice.id)]):
                raise UserError("Documento Duplicado.")
        return self.write({'state': 'E'})

    

    @api.multi
    def action_summary_cancel(self):
        if self.filtered(lambda summ: summ.state not in ['B','R','N','P']):
            raise UserError("Para cancelar este resumen, su estado debe ser: Borrador, Envío Erróneo, Rechazado o Pendiente de Envío")
        return self.write({'state': 'C'})

    @api.multi
    def action_summary_draft(self):
        if self.filtered(lambda inv: inv.state != 'C'):
            raise UserError("Para pasar a estado 'Borrador' el Resumen debe estar en estado 'Cancelado'.")
        return self.write({'state': 'B', 'date': False})


    @api.onchange('date_invoice')
    def onchange_calcute_cont(self):
        cont = 1
        n=0
        documets = self.env['efact.account_comunicacion_baja'].search([['state', '=', 'E'],['date_invoice', '=', self.date_invoice]])
        for document in documets:
            if cont < document.contador:
                cont = document.contador
            n = n +1
        if n!=0:
            self.contador = cont + 1
        else:
            self.contador = 1

    def _default_invoice_ids(self):
        invoices = []
        if self._context.get('default_invoice_ids', False):
            for document in self._context.get('default_invoice_ids'):
                invoices.append(self.env['account.invoice'].browse(document))
            return invoices

    invoice_ids = fields.One2many('account.invoice',"documento_baja_id",default=_default_invoice_ids)

    def _list_invoice_type(self):
        catalogs=self.env["einvoice.catalog.01"].search([])
        list=[]
        for cat in catalogs:
            list.append((cat.code,cat.name))
        return list

    def _default_invoice_type_code_id(self):
        if self._context.get('default_invoice_type_code_id', False):
            return self._context.get('default_invoice_type_code_id')

    invoice_type_code_id = fields.Selection(string="Tipo de Documento", 
                                            selection=_list_invoice_type, 
                                            default=_default_invoice_type_code_id,
                                            readonly=True, 
                                            states={'B': [('readonly', False)]},)


    def generar_comunicacion_baja(self):
        tipo_resumen="RA"
        now = datetime.now()
        data = {
            "tipoResumen": tipo_resumen,
            "fechaGeneracion": self.date_invoice,
            "idTransaccion": str(self.id),
            "resumen": {
                "id": self.contador,
                "tipoDocEmisor": self.company_id.partner_id.tipo_documento,
                "numDocEmisor": self.company_id.partner_id.vat,
                "nombreEmisor": self.company_id.partner_id.registration_name,
                "fechaReferente": self.date_invoice,
                "tipoFormatoRepresentacionImpresa": "GENERAL"
            }
        }

        data_detalle = []
        for document in self.invoice_ids:
            data_detalle.append({
                "serie": document.number[0:4],
                "correlativo": int(document.number[5:len(document.number)]),
                "tipoDocumento": document.invoice_type_code,
                "motivo": self.motivo
            })

        data['detalle'] = data_detalle

        return data

    @api.multi
    def action_summary_sent(self):
        self.enviar_comunicacion_baja()
        """
        to_open_invoices = self.filtered(lambda inv: inv.state != 'E')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['B']):
            raise UserError("Invoice must be in draft or Pro-forma state in order to validate it.")
        envio, msg = self.enviar_comunicacion_baja()
        if envio:
            if msg=="":
                for document in self.invoice_ids:
                    obj = self.env['account.invoice'].browse(document.id)
            self.write({'state': 'E'})
        if msg!="":
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': msg
                }
            }
        """
    def enviar_comunicacion_baja(self):
        token = generate_token_by_company(self.company_id,100000)
        data_doc = self.crear_json_baja()
        # os.system("echo '%s'"%("comunicacion baja"))
        # os.system("echo '%s'"%(json.dumps(data_doc)))
        response_env = enviar_doc_baja_url(self.company_id.endpoint,data_doc,token,self.company_id.tipo_envio)
        # os.system("echo '%s'"%(response_env))
        self.json_comprobante = json.dumps(data_doc, indent=4) 
        self.json_respuesta = json.dumps(response_env.json(), indent=4)
        if response_env.ok:
            response = response_env.json()
            result = response.get("result",False)
            if result:
                if result.get("data",False):
                    data = result["data"]
                    self.state = data['estadoEmision']
                    self.ticket = data['idTicket']
        else:
            recepcionado, state, msg_error = extraer_error(response_env)
            if recepcionado:
                self.state = state
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'custom.pop.message',
                    'target': 'new',
                    'context': {
                        'default_name': msg_error
                    }
                }
            else:
                return {
                    'name': 'Message',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'custom.pop.message',
                    'target': 'new',
                    'context': {
                        'default_name': msg_error
                    }
                }

    
    def crear_json_baja(self):
        data = {
            "tipoResumen": "RA",
            "fechaGeneracion": self.date_invoice,
            "idTransaccion": str(self.id),
            "resumen": {
                "id": self.contador,
                "tipoDocEmisor": self.company_id.partner_id.tipo_documento,
                "numDocEmisor": self.company_id.partner_id.vat,
                "nombreEmisor": self.company_id.partner_id.registration_name,
                "fechaReferente": self.date_invoice,
                "tipoFormatoRepresentacionImpresa": "GENERAL"
            }
        }

        data_detalle = []
        for document in self.invoice_ids:
            data_detalle.append({
                "serie": document.number[0:4],
                "correlativo": int(document.number[5:len(document.number)]),
                "tipoDocumento": document.invoice_type_code,
                "motivo": self.motivo
            })

        data['detalle'] = data_detalle

        return data

    def consulta_estado_comunicacion_baja(self):
        token = generate_token_by_company(self.company_id,100000)
        endpoint = self.company_id.endpoint
        data={
            "method":"Factura.consultaResumen",
            "kwargs":{
                "data":{
                    "ticket":self.ticket,
                    "tipoEnvio":int(self.company_id.tipo_envio),
                }
            }
        }
        headers = { 
            "Content-Type": "application/json",
            "Authorization" : token
        }
        r = requests.post(endpoint, headers=headers, data=json.dumps(data))
        
        # os.system("echo '%s'"%(json.dumps(data)))
        
        response = r.json()
        self.json_estado_comunicacion_baja = json.dumps(response,indent=4)
        result = response.get("result",False)

        # os.system("echo '%s'"%(json.dumps(response,indent=4)))

        if result:
            status =  result.get("status",False)
            code = result.get("code",False)
            if code == "env:Server":
                raise UserError(response["result"]["description"])
            
            if status:
                self.state = response["result"]["status"]
                self.descripcion_estado_com_baja = response["result"]["description"]
            else:
                raise UserError(json.dumps(response))
        else:
            raise UserError(json.dumps(response))
        