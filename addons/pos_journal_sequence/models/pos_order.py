# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools.profiler import profile
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    number = fields.Char(string='Number', readonly=True, copy=False)
    sequence_number = fields.Integer(string='Sequence Number', readonly=True, copy=False)
    invoice_journal = fields.Many2one('account.journal', string='Invoice Journal', readonly=True)
    from_pos = fields.Boolean(default=True)
    
    def _list_invoice_type(self):
        catalogs=self.env["einvoice.catalog.01"].search([])
        list=[]
        for cat in catalogs:
            list.append((cat.code,cat.name))
        return list

    #invoice_type_code_id = fields.Selection(string="Tipo de Documento",selection=_list_invoice_type)
    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        res['move_name'] = self.number
        res['journal_id']  = self.invoice_journal.id #or self.session_id.config_id.invoice_journal_id.id
        #res['invoice_type_code_id'] = self.invoice_type_code_id

        if self.invoice_journal and self.sequence_number:
            self.invoice_journal.sequence_id.pos_next(self.sequence_number+1) 
        return res
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['number']=ui_order.get('number', False)
        res['invoice_journal']=ui_order.get('invoice_journal', False)
        res['sequence_number']=ui_order.get('sequence_number', 0)
        #res['invoice_type_code_id']=ui_order.get('invoice_type_code_id', False)
        return res
   
    # @api.model
    # def create_from_ui(self, orders):
    #     _logger.info(orders)
    #     for i, order in enumerate(orders):
    #         if order.get('data', {}).get('invoice_journal'): #and order.get('data', {}).get('invoice_type_code_id'):
    #             orders[i]['to_invoice']=True
    #     _logger.info(orders)
    #     objs = super(PosOrder, self).create_from_ui(orders)
    #     arr=[]
    #     for o in objs:
    #         #digestvalue=self.env["pos.order"].browse(o).invoice_id.digestvalue
    #         arr.append(o)
    #     _logger.info(arr)
    #     return arr
    
  
    @api.multi
    def action_pos_order_invoice_boleta(self):
        Invoice = self.env['account.invoice']

        for order in self:
            order.from_pos = False
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Debes proporcionar un cliente para generar el Comprobantes.'))
                
            journal_objs = self.env["account.journal"].search([["invoice_type_code_id","=","03"],["tipo_envio","=",self.company_id.tipo_envio]])
            if len(journal_objs)>0:
                order.invoice_journal = journal_objs[0].id

            prepare_invoice = order._prepare_invoice()
            prepare_invoice.update({"invoice_type_code_id":"03"})
            invoice = Invoice.new(prepare_invoice)
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _("Este comprobante ha sido creado desde la sesión de punto de venta: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

            new_invoice.with_context(local_context).sudo().compute_taxes()
            order.sudo().write({'state': 'invoiced'})

        if not Invoice:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': Invoice and Invoice.ids[0] or False,
        }

    @api.multi
    def action_pos_order_invoice_factura(self):
        Invoice = self.env['account.invoice']

        for order in self:
            order.from_pos = False
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Debes proporcionar un cliente para generar el Comprobantes.'))
            
            journal_objs = self.env["account.journal"].search([["invoice_type_code_id","=","01"],["tipo_envio","=",self.company_id.tipo_envio]])
            if len(journal_objs)>0:
                order.invoice_journal = journal_objs[0].id

            prepare_invoice = order._prepare_invoice()
            prepare_invoice.update({"invoice_type_code_id":"01"})
            invoice = Invoice.new(prepare_invoice)
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _("Este comprobante ha sido creado desde la sesión de punto de venta: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

            new_invoice.with_context(local_context).sudo().compute_taxes()
            order.sudo().write({'state': 'invoiced'})

        if not Invoice:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': Invoice and Invoice.ids[0] or False,
        }
