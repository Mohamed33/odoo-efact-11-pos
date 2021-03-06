# -*- coding: utf-8 -*-

from odoo import models, fields, api

class webservice(models.Model):
	_inherit = 'account.payment'

	detalle = fields.Text("Detalle")
	id_transaccion = fields.Char('ID de transaccion')
	procedencia = fields.Char("Procedencia")
