# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_default_warehouse(self):
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        return warehouse_id

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
            'state': 'draft',
            'origin': invoice.number,
        })

        invoice.picking_id = picking_id.id
        for line in invoice.invoice_line_ids:
            if line.product_id and line.product_id.type != 'service':
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
        '''picking_id.action_confirm()
        picking_id.action_assign()
        if picking_id.state != 'assigned':
            picking_id.force_assign()
        picking_id.button_validate()'''