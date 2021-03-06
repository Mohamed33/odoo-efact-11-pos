# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import Warning,UserError
from odoo.http import request
import os
import json

class AccountInvoice(models.Model):
    _inherit= 'account.invoice'


    @api.model
    def _default_picking_receive(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    @api.model
    def _default_picking_transfer(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return types[0]
    
    picking_count = fields.Integer(string="Count", copy=False)
    move_count = fields.Integer(string="Count" ,copy=False)
    #invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id")
    invoice_move_ids = fields.One2many('stock.move', 'invoice_id',string="Move Id")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',default=_default_picking_receive, 
                                      help="Esto determinará el tipo de operación de ingreso de Mercancía")
    picking_transfer_id = fields.Many2one('stock.picking.type', 'Deliver To', default=_default_picking_transfer, 
                                          help="Esto determinará el tipo de operación de envío de Mercancía")


    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
        ('done', 'Received'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.multi
    def action_stock_receive(self):
        move_list = []
        for order in self:
            if not order.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if not self.invoice_picking_id:
                moves = order.invoice_line_ids.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(order)
                for m in moves:
                	move_list.append(m.id)
                order.move_count = len(move_list)


    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()
        if self.origin == False:
            """
            if self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc").create_move:
                self.action_stock_receive()
            if self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc").create_picking:
            """
            warehouse_obj = self.env['stock.warehouse']
            company_id = self.env['res.company']._company_default_get('picking.from.invoice')
            ware_ids = warehouse_obj.search([('company_id', '=', company_id.id)])
            if not ware_ids:
                raise Warning('You cannot  create picking because you not\
                    have a warehouse!')
            for invoice in self:
                if invoice.type in ('in_invoice', 'out_invoice'):
                    #Se emite una factura de venta y se genera un documento de salida de mercadería
                    if invoice.type == 'in_invoice': 
                        pick_name = self.env['stock.picking.type'].browse(invoice.picking_type_id.id).sequence_id.next_by_id()
                        picking = self.env['stock.picking'].create({
                                                                'partner_id':invoice.partner_id.id,
                                                                'name': pick_name,
                                                                'tiene_guia_remision': invoice.numero_guia_remision != False,
                                                                'numero_guia':invoice.numero_guia_remision,
                                                                'origin':invoice.move_name,
                                                                'picking_type_id': invoice.picking_type_id.id,
                                                                'state': 'draft',
                                                                'move_type': 'direct',
                                                                'note': invoice.comment,
                                                                'company_id': invoice.company_id.id,
                                                                'location_id': invoice.picking_type_id.default_location_src_id.id,
                                                                'location_dest_id': invoice.picking_type_id.default_location_dest_id.id,
                                                                })
                    #Se realiza una factura de compra y se genera un documento de salida de mercadería
                    else:
                        pick_name = self.env['stock.picking.type'].browse(invoice.picking_transfer_id.id).sequence_id.next_by_id()
                        picking = self.env['stock.picking'].create({
                                                                    'partner_id':invoice.partner_id.id,
                                                                    'name': pick_name,
                                                                    'tiene_guia_remision': invoice.numero_guia_remision != False,
                                                                    'origin':invoice.move_name,
                                                                    'numero_guia':invoice.numero_guia_remision,
                                                                    'picking_type_id': invoice.picking_transfer_id.id,
                                                                    'state': 'draft',
                                                                    'move_type': 'direct',
                                                                    'note': invoice.comment,
                                                                    'company_id': invoice.company_id.id,
                                                                    'location_id': invoice.picking_transfer_id.default_location_src_id.id,
                                                                    'location_dest_id': invoice.picking_transfer_id.default_location_dest_id.id,
                                                                    })
                
                    invoice.invoice_picking_id = picking.id
                    invoice.picking_count = len(picking)
                    moves = invoice.invoice_line_ids.filtered(lambda r: r.product_id.type in ['product','consu']).create_stock_moves_transfer(picking)
                    move_ids = moves._action_confirm()
                    move_ids._action_assign()
                    picking.action_assign()
                    picking.do_transfer()
                    

                if invoice.type in ('in_refund', 'out_refund'):
                    #Se realiza una nota de crédita de factura de compra y se genera un documento de entrada de mercadería
                    if invoice.type == 'in_refund':
                        pick_name = self.env['stock.picking.type'].browse(invoice.picking_transfer_id.id).sequence_id.next_by_id()
                        picking = self.env['stock.picking'].create({
                                                                'partner_id':invoice.partner_id.id,
                                                                'name': pick_name,
                                                                'origin':invoice.move_name,
                                                                'picking_type_id': invoice.picking_type_id.id,
                                                                'state': 'draft',
                                                                'move_type': 'direct',
                                                                'tiene_guia_remision': invoice.numero_guia_remision != False,
                                                                'note': invoice.comment,
                                                                'numero_guia':invoice.numero_guia_remision,
                                                                'company_id': invoice.company_id.id,
                                                                'location_id': request.env.ref("stock.stock_location_suppliers").id,
                                                                'location_dest_id': invoice.picking_type_id.default_location_dest_id.id,
                                                                })
                    #Se emite una Nota de crédito de factura de venta y se genera un documento de entrada de mercadería
                    elif invoice.type == 'out_refund':
                        pick_name = self.env['stock.picking.type'].browse(invoice.picking_type_id.id).sequence_id.next_by_id()
                        data = {
                                'partner_id':invoice.partner_id.id,
                                'name': pick_name,
                                'origin': invoice.number,
                                'picking_type_id': invoice.picking_transfer_id.id,
                                'state': 'draft',
                                'numero_guia':invoice.numero_guia_remision,
                                'move_type': 'direct',
                                'note': invoice.comment,
                                'company_id': invoice.company_id.id,
                                'location_id': request.env.ref("stock.stock_location_customers").id,
                                'location_dest_id': invoice.picking_type_id.default_location_dest_id.id,
                                }
                        os.system("echo '%s'"%(json.dumps(data)))
                        picking = self.env['stock.picking'].create(data)
                    
                    invoice.invoice_picking_id = picking.id
                    invoice.picking_count = len(picking)
                    moves = invoice.invoice_line_ids.filtered(lambda r: r.product_id.type in ['product','consu']).create_stock_moves_transfer(picking)
                    move_ids = moves._action_confirm()
                    move_ids._action_assign()
                    picking.action_assign()
                    picking.do_transfer()

    @api.multi
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.invoice_picking_id.id)]
        pick_ids = sum([self.invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result

    @api.multi
    def action_view_move(self):
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', 'in', list(map(int,self.invoice_move_ids)))]
        move_ids = list(map(int,self.invoice_move_ids))
        tree_view_id = self.env.ref('stock.view_move_tree', False)
        form_view_id = self.env.ref('stock.view_move_form', False)
        result['views'] = [(tree_view_id and tree_view_id.id or False, 'tree'),(form_view_id and form_view_id.id or False, 'form')]
        return result

class AccountConfig(models.TransientModel):
    _inherit = "res.config.settings"


    create_move = fields.Boolean('Create Stock Move From Invoice')
    create_picking = fields.Boolean('Create Stock Picking From Invoice')

    @api.model
    def default_get(self, fields_list):
        res = super(AccountConfig, self).default_get(fields_list)
        create_move_search = self.search([], limit=1, order="id desc").create_move
        create_picking_search = self.search([], limit=1, order="id desc").create_picking
        res.update({'create_move':create_move_search,
					'create_picking':create_picking_search,
                    })
        return res

class SupplierInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if picking.type == 'out_invoice':
                pick = picking.picking_transfer_id.id
                location = line.invoice_id.picking_transfer_id.default_location_src_id.id
                des_location = line.invoice_id.partner_id.property_stock_customer.id
            else:
                pick = picking.picking_type_id.id
                des_location = line.invoice_id.picking_type_id.default_location_dest_id.id
                location = line.invoice_id.partner_id.property_stock_supplier.id
            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'location_id': location,
                'location_dest_id': des_location,
                'move_dest_id': False,
                'state': 'draft',
				'invoice_id':picking.id,
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': pick,
                'procurement_id': False,
                'route_ids': 1 and [
                    (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done

    def create_stock_moves_transfer(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if line.invoice_id.type == 'out_invoice':
                os.system("echo 'out_invoice' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = line.invoice_id.picking_transfer_id.default_location_src_id.id
                des_location = line.invoice_id.partner_id.property_stock_customer.id
            elif line.invoice_id.type == 'out_refund':
                os.system("echo 'out_refund' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = request.env.ref("stock.stock_location_customers").id
                des_location = line.invoice_id.picking_transfer_id.default_location_src_id.id
            elif line.invoice_id.type == 'in_refund':
                os.system("echo 'in_refund' ")
                pick = line.invoice_id.picking_transfer_id.id
                location = request.env.ref("stock.stock_location_suppliers").id
                des_location = line.invoice_id.picking_transfer_id.default_location_src_id.id
            elif line.invoice_id.type == 'in_invoice':
                os.system("echo 'in_invoice' ")
                pick = picking.picking_type_id.id
                des_location = line.invoice_id.picking_type_id.default_location_dest_id.id
                location = line.invoice_id.partner_id.property_stock_supplier.id

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'location_id': location,
                'location_dest_id': des_location,
                'picking_id': picking.id,
                #'move_dest_id': False,
                'state': 'draft',
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': picking.picking_type_id.id,
                #'procurement_id': False,
                'route_ids': 1 and [
                    (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            os.system("echo '%s' "%(json.dumps(template)))
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done = moves.create(template)
        return done

class stockMove(models.Model):
    _inherit = "stock.move"


    invoice_id = fields.Many2one('account.invoice',string='Invoice')
