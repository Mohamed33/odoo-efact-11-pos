from odoo import fields, models, api ,_
from odoo.http import request
from datetime import datetime
import os
from odoo.tools.profiler import profile
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    branch_id = fields.Many2one("res.branch","Sucursal")
    ruta_ids = fields.Many2many("cn.ruta",string="Rutas")
    referencia_nota_ids = fields.One2many("account.invoice","refund_invoice_id")
    guia_remision_ids = fields.Many2many("view.guia.remision.consolidado")

    def get_naomis_partner(self):
        for res in self:
            res.naomis_partner_id = res.partner_id

   
    naomis_partner_id = fields.Many2one('res.partner', string='Cliente', compute=get_naomis_partner)
    
    @api.multi
    def generar_nota_credito(self):
        if not self.number:
            self.action_invoice_open()
        ref = request.env.ref("account.invoice_form")
        inv_lines2 = []
        for il1 in self.invoice_line_ids:
            obj = il1.copy(default={
                "invoice_id": ""
            })
            inv_lines2.append(obj.id)
        #print(str(self.number[0:4]) + " - " + str(int(self.number[5:len(self.number)])))
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "target": "self",
            "view_id": ref.id,
            "view_mode": "form",
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_refund_invoice_id': self.id,
                'default_date_invoice': datetime.now().strftime("%Y-%m-%d"),
                'default_payment_term_id': self.payment_term_id.id,
                'default_invoice_line_ids': inv_lines2,
                'default_new_invoice': False,
                'default_type': 'out_refund',
                'journal_type': 'sale',
                'default_user_id':self.user_id.id,
                'default_invoice_type_code': '07',
                'default_number': 'Nota de Crédito'},
            "domain": [('type', 'in', ('out_invoice', 'out_refund')), ('invoice_type_code', '=', '07')]
        }

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        """ Notify newly subscribed followers of the last posted message.
            :param partner_ids : the list of partner to add as needaction partner of the last message
                                 (This excludes the current partner)
        """
        return
        """
        if not partner_ids:
            return

        if self.env.context.get('mail_auto_subscribe_no_notify'):
            return

        if 'active_domain' in self.env.context:
            ctx = dict(self.env.context)
            ctx.pop('active_domain')
            self = self.with_context(ctx)

        for record in self:
            record.message_post_with_view(
                'mail.message_user_assigned',
                composition_mode='mass_mail',
                partner_ids=[(4, pid) for pid in partner_ids],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False, # override accidental context defaults
                subtype_id=self.env.ref('mail.mt_note').id) 
        """


    @api.model
    def create_move(self, invoice, picking_type_id, location_id, location_dest_id):
        StockMove = self.env['stock.move']
        picking_id = self.env['stock.picking'].create({
            'partner_id': invoice.partner_id.id,
            'date': fields.datetime.now(), 
            'company_id': invoice.company_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'origin': invoice.number,
        })

        _logger.info(picking_id)

        invoice.picking_id = picking_id.id
        for line in invoice.invoice_line_ids:
            if line.product_id and line.product_id.is_combo:
                for cp in line.product_id.combo_product_id:
                    StockMove.create({
                        'product_id': cp.product_id.id,
                        'product_uom_qty': cp.product_quantity*line.quantity,
                        'product_uom': cp.uom_id.id,
                        'date': fields.datetime.now(),
                        'date_expected': fields.datetime.now(),
                        'picking_id': picking_id.id,
                        'state': 'draft',
                        'name': line.name,
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id,
                        'quantity_done': cp.product_quantity*line.quantity
                    })
            elif line.product_id and line.product_id.type != 'service':
                StockMove.create({
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'date': fields.datetime.now(),
                    'date_expected': fields.datetime.now(),
                    'picking_id': picking_id.id,
                    'state': 'draft',
                    'name': line.name,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'quantity_done': line.quantity,
                })
        picking_id.action_confirm()
        picking_id.action_assign()
        if picking_id.state != 'assigned':
            picking_id.force_assign()
        picking_id.button_validate()

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'


    def _set_naomis_price_subtotal(self):
        for res in self:
            res.naomis_price_subtotal = res.price_subtotal2 * -1 if res.invoice_id.journal_id.invoice_type_code_id in ['07'] else res.price_subtotal2

    naomis_price_subtotal = fields.Float(string='Precio Total', compute=_set_naomis_price_subtotal)