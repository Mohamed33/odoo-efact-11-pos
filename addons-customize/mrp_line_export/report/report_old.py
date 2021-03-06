# -*- coding: utf-8 -*-

import datetime
from datetime import datetime, timedelta
import pytz

from odoo import models, fields
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

from itertools import groupby

import logging
logger = logging.getLogger(__name__)


class StockReportXls(ReportXlsx):

    def convert_date(self, s):
        if s:
            return "%s/%s/%s" % (s[8:10], s[5:7], s[0:4])
        else:
            return ""

    def generate_xlsx_report(self, workbook, data, wizard):
        
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')  
        date_from = fields.Datetime.from_string(wizard.date_start) 
        date_from = user_tz.localize(date_from) 
        date_from = date_from.astimezone(pytz.timezone('UTC')) 
        date_from = fields.Datetime.to_string(date_from) 

        date_to = fields.Datetime.from_string(wizard.date_end) + timedelta(days=1, seconds=-1)
        date_to = user_tz.localize(date_to)
        date_to = date_to.astimezone(pytz.timezone('UTC'))
        date_to = fields.Datetime.to_string(date_to)

        format_pos = workbook.add_format({'bold': True, 'font_color': 'black', 'font_size': 9, })
        format_pos.set_align('center')
        format_pos.set_text_wrap()   
        format_pos.set_font_color('#ffffff')  
        format_pos.set_bg_color('#0b79cb')   

        worksheet = workbook.add_worksheet('Lista de insumos')

        worksheet.set_column('A:A', 8)   # Ancho de la celda A
        worksheet.set_column('B:B', 30)  # Ancho de la celda B
        worksheet.set_column('C:C', 14)  # B
        worksheet.set_column('D:D', 10)  # D
        worksheet.set_column('E:E', 20)  # E
        worksheet.set_column('F:F', 15)  # F

        bold = workbook.add_format({'bold': True})
        worksheet.merge_range('B2:E2', 'REPORTE: ' + str(self.convert_date(wizard.date_start)) + ' - ' + str(
            self.convert_date(wizard.date_end)), bold)

        worksheet.write('A5', 'FAMILIA', format_pos)
        worksheet.write('B5', 'DESCRIPCION', format_pos)
        worksheet.write('C5', 'CANT.', format_pos)
        worksheet.write('D5', 'UNID.', format_pos)
        worksheet.write('E5', 'PRECIO (S/)', format_pos)
        worksheet.write('F5', 'TOTAL COSTO (S/)', format_pos)

        format_cell = workbook.add_format({'font_size': 9, 'bold': False})
        format_cell.set_num_format('#,##0.00')

        mrp_lines = self.env['stock.move'].search([('raw_material_production_id.date_planned_start', '>=', date_from),
                                                   ('raw_material_production_id.date_planned_start', '<=', date_to)])
        # logger.error('Viendo el valor de line: %s', mrp_lines)
        list_items_repeated = []

        if mrp_lines:
            for line in mrp_lines:
                list_items_repeated.append([line.product_id.id, line.product_uom_qty])

        list_items_no_repeated = []
        for i, g in groupby(sorted(list_items_repeated, reverse=True), key=lambda x: x[0]):
            list_items_no_repeated.append([i, sum(v[1] for v in g)])

        list_code = []
        for producto in list_items_no_repeated:
            prod = self.env['product.product'].search([('id', '=', producto[0])])
            list_code.append([prod.default_code, prod, producto[1]])
        logger.error('Viendo list_code: %s', list_code)


        lista_final = sorted(list_code)
        logger.error('Viendo list_code: %s', lista_final)

        columna = 5
        for producto in lista_final:
            columna = columna + 1

            worksheet.write('A' + str(columna), producto[1].default_code or '', format_cell)
            worksheet.write('B' + str(columna), producto[1].name or '', format_cell)
            worksheet.write('C' + str(columna), producto[2] or '', format_cell)
            worksheet.write('D' + str(columna), producto[1].uom_id.name or '', format_cell)
            worksheet.write('E' + str(columna), producto[1].standard_price or '0', format_cell)
            worksheet.write('F' + str(columna), producto[2] * producto[1].standard_price or '0', format_cell)

StockReportXls('report.mrp_line_export.mrp_line_export_xlsx', 'mrp.line.export.wizard')
