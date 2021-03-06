# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api

SC_STATES =[('draft','Borrador'),('open','Abierto'), ('done','Hecho')]
class stock_card(models.Model):
    _name 		= "kardex.stock_card"
    _rec_name 	= "product_id"

    ref =    fields.Char("Número")
    date_start =    fields.Date("Fecha de inicio", required=True, default = lambda self: time.strftime("%Y-%m-%d"))
    date_end =    fields.Date("Fecha de Fin", required=True, default = lambda self: time.strftime("%Y-%m-%d"))
    location_id =    fields.Many2one('stock.location', 'Ubicación', required=True)
    product_id =    fields.Many2one('product.product', 'Producto', required=True)
    #lot_id =    fields.Many2one('stock.production.lot', 'Serial Number')
    #expired_date = fields.Datetime(related="lot_id.life_date")
    #expired_date =    fields.Related('lot_id', "life_date", string="Expired Date", type="date", relation="stock.production.lot")
    line_ids =    fields.One2many('kardex.stock_card_line','stock_card_id','Detalle', ondelete="cascade")
    state =    fields.Selection(SC_STATES,'Estado',readonly=True,required=True,default="draft")
    user_id =    fields.Many2one('res.users', 'Responsable')


    @api.multi
    def action_calculate(self):
		# kosongkan stock_card_line
		# cari stock move product_id dan location_id, start_date to end_date
		# insert into stock_card_line
		# jika keluar dari location (source_id) maka isi ke qty_out
		# jika masu ke location (dest_id) maka isi ke qty_in
		# hitung qty_balance = qty_start + qty_in - qty_out 
		# start balance dihitung dari total qty stock move sebelum start_date

        stock_move = self.env['stock.move']
        stock_card_line = self.env['kardex.stock_card_line']
        product = self.env['product.product']

        for sc in self:
            self.env.cr.execute("delete from kardex_stock_card_line where stock_card_id=%s" % sc.id)

            qty_start = 0.0
            qty_balance = 0.0
            qty_in = 0.0
            qty_out = 0.0
            product_uom = False

            ### cari lot id moves
            #lot_id = sc.lot_id
            """
            sql2 = "select move_id from stock_quant_move_rel qm " \
                    "join stock_quant q on qm.quant_id = q.id "\
                    "where q.lot_id = %s" % (lot_id.id)
            """
            sql2 = "select id from stock_move where product_id = {}".format(sc.product_id.id)

            self.env.cr.execute(sql2)
            res = self.env.cr.fetchall()
            move_ids = []
            if res and res[0]!= None:
                for move in res:
                    move_ids.append(move[0])

            ## beginning balance in 
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s " \
                    "and date < '%s' and location_dest_id=%s " \
                    "and id in %s "\
                    "and state='done'" %(
                sc.product_id.id, sc.date_start, sc.location_id.id, str(tuple(move_ids)))
            self.env.cr.execute(sql)
            res = self.env.cr.fetchone()
            if res and res[0]!= None:
                qty_start = res[0]

            ## beginning balance out
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s and date < '%s' and location_id=%s and state='done'" %(
                sc.product_id.id, sc.date_start, sc.location_id.id)
            self.env.cr.execute(sql)
            res = self.env.cr.fetchone()
            if res and res[0]!= None:
                qty_start = qty_start - res[0]
            
            ## product uom
            # import pdb;pdb.set_trace()
            prod = product.browse([sc.product_id.id])
            product_uom = prod.uom_id 


            data = {
                "stock_card_id"	: sc.id,
                "date"			: False,
                "qty_start"		: False,
                "qty_in"		: False,
                "qty_out"		: False,
                "qty_balance"	: qty_start,	
                "product_uom_id": product_uom.id,	
            }
            stock_card_line.create(data)

            ##mutasi
            sm_ids = stock_move.search([
                '|',
                ('location_dest_id','=',sc.location_id.id),
                ('location_id','=',sc.location_id.id),
                ('product_id', 	'=' , sc.product_id.id),
                ('date', 		'>=', sc.date_start),
                ('date', 		'<=', sc.date_end),
                ('state',		'=',  'done'),
                ('id',			'in', move_ids)

            ], order='date asc')

            for sm in sm_ids:

                qty_in = 0.0
                qty_out = 0.0

                #uom conversion factor
                if product_uom.id != sm.product_uom.id:
                    factor =  product_uom.factor / sm.product_uom.factor 
                else:
                    factor = 1.0

                if sm.location_dest_id == sc.location_id:	#incoming, dest = location
                    qty_in = sm.product_uom_qty  * factor				
                elif sm.location_id == sc.location_id:		#outgoing, source = location
                    qty_out = sm.product_uom_qty * factor

                qty_balance = qty_start + qty_in - qty_out

                name = sm.name if sm.name!=prod.display_name else ""
                partner_name = sm.partner_id.name if sm.partner_id else ""
                notes = sm.picking_id.note or ""
                po_no = sm.group_id.name if sm.group_id else ""
                origin = sm.origin or ""
                finish_product = ""

                if "MO" in origin:
                    mrp = self.pool.get('mrp.production')
                    mo_id = mrp.search([("name","=",origin)])
                    mo = mrp.browse(mo_id)
                    finish_product = "%s:%s"%(mo[0].product_id.name,mo[0].batch_number) if mo else ""


                data = {
                    "stock_card_id"	: sc.id,
                    "move_id"		: sm.id,
                    "picking_id"	: sm.picking_id.id,
                    "date"			: sm.date,
                    "qty_start"		: qty_start,
                    "qty_in"		: qty_in,
                    "qty_out"		: qty_out,
                    "qty_balance"	: qty_balance,	
                    "product_uom_id": product_uom.id,	
                    "name"			: "%s/ %s/ %s/ %s/ %s/ %s" % (name,finish_product,partner_name,po_no,notes,origin),
                }
                stock_card_line.create(data)
                qty_start = qty_balance

        
class stock_card_line(models.Model):
    _name 		= "kardex.stock_card_line"
    
    name = fields.Char("Descripción")
    stock_card_id = fields.Many2one('kardex.stock_card', 'Kardex')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    picking_id = fields.Many2one('stock.picking', 'Movimiento')
    date = fields.Date("Fecha")
    qty_start = fields.Float("Saldo Inicial")
    qty_in = fields.Float("Ingreso")
    qty_out = fields.Float("Salida")
    qty_balance = fields.Float("Saldo Final")
    product_uom_id = fields.Many2one('product.uom', 'UoM')
    invoice_id = fields.Many2one("account.invoice",compute="compute_get_invoice")

    @api.multi
    @api.depends("move_id")
    def compute_get_invoice(self):
        for record in self:
            move_id = record.move_id
            if len(move_id):
                sale_line = move_id.sale_line_id
                if sale_line:
                    invoice_line = sale_line.invoice_lines
                    if invoice_line:
                        record.invoice_id = sale_line.invoice_lines.invoice_id.id