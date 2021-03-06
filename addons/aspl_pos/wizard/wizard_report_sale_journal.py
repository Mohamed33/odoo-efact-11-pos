# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import xlwt
from io import BytesIO as cStringIO
import base64
from datetime import datetime, timedelta
import pytz


class wizard_report_sale_journal(models.TransientModel):
    _name = 'wizard.report.sale.journal'

    session_id = fields.Many2one('pos.session', string="Session")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    location_id = fields.Many2one("stock.location","Location")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='File Name', readonly=True)
    data = fields.Binary(string='File', readonly=True)

    @api.multi
    def generate_xls_report(self):
        domain = []
        if not self.session_id and not self.location_id:
            raise Warning(_('You have to select atleast one option from Sesssion Or Location '))
        if self.session_id:
            domain.append(('session_id', '=', self.session_id.id))
        if self.start_date:
            domain.append(('date_order', '>=', self.get_datetime_timezone(self.start_date + " 00:00:00")))
        if self.end_date:
            domain.append(('date_order', '<=', self.get_datetime_timezone(self.end_date + " 23:59:59")))

        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))

        pos_order_ids = self.env['pos.order'].search(domain)
        sale_order_ids = self.env['sale.order'].search(domain)

        if not pos_order_ids and not sale_order_ids:
            raise Warning(_('No Record found.'))
        styleP = xlwt.XFStyle()
        stylePC = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
        stylePC.pattern = pattern
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        styleP.alignment = alignment
        stylePC.alignment = alignment
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Report Sales Journal")
        worksheet.write(0, 0, 'ORDER REFERENCE', style=stylePC)
        worksheet.write(0, 1, 'RECEIPT REFERENCE', style=stylePC)
        worksheet.write(0, 2, 'DOCUMENT TYPE', style=stylePC)
        worksheet.write(0, 3, 'NAME OF CUSTOMER', style=stylePC)
        worksheet.write(0, 4, 'OUT / IN', style=stylePC)
        worksheet.write(0, 5, 'EXCHANGE OLD BATTERY', style=stylePC)
        worksheet.write(0, 6, 'MODELO', style=stylePC)
        worksheet.write(0, 7, 'CODIGO BATTERY', style=stylePC)
        worksheet.write(0, 8, 'ORDER DATE', style=stylePC)
        worksheet.write(0, 9, 'SELLER OR CASHIER', style=stylePC)
        worksheet.write(0, 10, 'TOTAL', style=stylePC)
        worksheet.write(0, 11, 'STATE', style=stylePC)
        worksheet.write(0, 12, 'SESSION', style=stylePC)
        worksheet.write(0, 13, 'NÚMERO DE COMPROBANTE', style=stylePC)
        worksheet.write(0, 14, 'ESTADO EMISIÓN', style=stylePC)
        state_dict = {'draft': 'New', 'cancel': 'Cancelled', 'paid': 'Paid', 'done': 'Posted', 'invoiced': 'Invoiced', 'sale': 'Confirm'}
        for col_number in range(0, 14):
            worksheet.col(col_number).width = 5200
        rows = 1
        grand_total = 0
        # pos_order
        for order in pos_order_ids:
            for line in order.lines:
                if line.back_order:
                    document_type = "PRODUCT RETURN"
                elif order.state == "invoiced":
                    document_type = "INVOICE"
                else:
                    document_type = "TICKET"
                worksheet.write(rows, 0, order.name)
                worksheet.write(rows, 1, order.pos_reference)
                worksheet.write(rows, 2, document_type)
                worksheet.write(rows, 3, order.partner_id and order.partner_id.name or "")
                worksheet.write(rows, 4, 1 if line.stock_income else -1, style=styleP)
                worksheet.write(rows, 5, "OK" if line.exchange_product else "", style=styleP)
                worksheet.write(rows, 6, line.product_id.name, style=styleP)
                worksheet.write(rows, 7, line.prodlot_id.name if line.prodlot_id else "", style=styleP)
                worksheet.write(rows, 8, self.get_datetime_timezone(order.date_order, fetch_argu=True))
                worksheet.write(rows, 9, order.user_id.name or "")
                worksheet.write(rows, 10, line.price_subtotal_incl, style=styleP)
                worksheet.write(rows, 11, state_dict[order.state])
                worksheet.write(rows, 12, order.session_id.name)
                worksheet.write(rows, 13, order.invoice_id.move_name)
                worksheet.write(rows, 14, order.invoice_id.estado_emision)
                grand_total += line.price_subtotal_incl
                rows += 1
            rows += 1
        # sale_order
        for order in sale_order_ids:
            for line in order.order_line:
                worksheet.write(rows, 0, order.name)
                worksheet.write(rows, 1, '-')
                worksheet.write(rows, 2, "SALE ORDER")
                worksheet.write(rows, 3, order.partner_id and order.partner_id.name or "")
                worksheet.write(rows, 4, -1, style=styleP)
                worksheet.write(rows, 5, "", style=styleP)
                worksheet.write(rows, 6, line.product_id.name, style=styleP)
                worksheet.write(rows, 7, line.lot_id.name if line.lot_id else "", style=styleP)
                worksheet.write(rows, 8, self.get_datetime_timezone(order.date_order, fetch_argu=True))
                worksheet.write(rows, 9, order.user_id.name or "")
                worksheet.write(rows, 10, line.price_subtotal, style=styleP)
                worksheet.write(rows, 11, state_dict[order.state])
                worksheet.write(rows, 12, order.session_id.name)
                grand_total += line.price_subtotal
                rows += 1
            rows += 1
        for col_number in range(0, 13):
            if col_number == 9:
                worksheet.write(rows, 9, "Total", style=stylePC)
            elif col_number == 10:
                worksheet.write(rows, 10, grand_total, style=stylePC)
            else:
                worksheet.write(rows, col_number, "", style=stylePC)
        file_data = cStringIO()
        workbook.save(file_data)
        session_name = '_'+ self.session_id.name if self.session_id else ""
        stock_name = ''
        if self.location_id:
            stock_name = '_'
            if self.location_id.location_id:
                stock_name +=  self.location_id.location_id.name + '/'
            stock_name += self.location_id.name
        # stock_name = '_'+ self.location_id.name if self.location_id else ""
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'reporte_diario_ventas'+session_name+''+stock_name+'.xls'
        })
        return {
            'name': 'Report Sales Journal',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.report.sale.journal',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    @api.multi
    def get_datetime_timezone(self, var_date, fetch_argu=None):
        if self._context and self._context.get('tz'):
            tz = pytz.timezone(self._context.get('tz'))
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if fetch_argu:
            if sign == '+':
                var_date = (datetime.strptime(var_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
            if sign == '-':
                var_date = (datetime.strptime(var_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            if sign == '-':
                var_date = (datetime.strptime(var_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
            if sign == '+':
                var_date = (datetime.strptime(var_date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return var_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: