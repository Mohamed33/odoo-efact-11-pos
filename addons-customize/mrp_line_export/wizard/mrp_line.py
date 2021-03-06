# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

import logging
logger = logging.getLogger(__name__)

class PosReport(models.TransientModel):
    _name = 'mrp.line.export.wizard'

    date_start = fields.Date(string="Fecha Inicial", required=True)
    date_end = fields.Date(string="Fecha Final", required=True)

    @api.multi
    def mrp_line_export(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'mrp.line.export.wizard'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        report_obj = self.env.ref("mrp_line_export.mrp_line_export_xlsx")
        return report_obj.report_action([],data=datas)
        


