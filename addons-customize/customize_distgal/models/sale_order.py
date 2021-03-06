# -*- coding: utf-8 -*-
from odoo.exceptions import UserError,AccessError
from odoo import fields,models,api,_
import json
import time
import os
from odoo.tools.profiler import profile


class SaleOrder(models.Model):
    _inherit = "sale.order"

    district_id = fields.Many2one("res.country.state",related="partner_id.district_id")
    street = fields.Char("Dirección",related="partner_id.street")