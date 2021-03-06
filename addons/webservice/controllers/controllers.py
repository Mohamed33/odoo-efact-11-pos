# -*- coding: utf-8 -*-
from odoo import http
from werkzeug.utils import redirect
import time
import math
import json


class Webservice(http.Controller):
	@http.route('/webservice/api-docs', auth='public')
	def index(self, **kw):
		return redirect('/webservice/static/api-docs.html')

	def _request_validation(self, data):
		# Validacion de data
		if data is None:
			return "No se ah encontrado el parametro data."
		if type(data)!=dict:
			return "Se espera que parametro data sea un diccionario."

		# Validacion de datos de cliente
		if 'cliente_id' not in data:
			return "cliente_id no encontrado."
		if type(data['cliente_id']) != int:
			return "cliente_id debe ser un numero entero"
		partner = http.request.env['res.partner'].search([['id', '=', data['cliente_id']]])
		if not partner:
			return "Cliente no encontrado"
		
		# Validacion de moneda
		if "moneda" not in data:
			data['moneda'] = "PEN"
		currency = http.request.env['res.currency'].search([['name', '=', data['moneda']]])
		if not currency:
			return "Codigo de moneda no encontrado"
		data["moneda"] = currency.id

		# Validacion de journal
		if "journal_id" not in data:
			return "Se espera el parametro journal_id como entero valido"

		journal = http.request.env['account.journal'].search([['id', '=', data['journal_id']]])
		if journal.invoice_type_code_id not in ["01", "03"]:
			return "journal_id invalido"

		# Validacion del tipo de operacion
		if "tipo_operacion" not in data:
			return "Falta especificar tipo_operacion"
		tp_op = data['tipo_operacion']
		if tp_op not in ['01', '02']:
			return "tipo_operacion invalido."
		#data['tipo_afectacion_igv']=http.request.env['einvoice.catalog.07'].search([['code', '=', '10' if tp_op == '01' else '40']]).id
		
		if tp_op == "01":
			data["impuesto_id"] = 1
		elif tp_op == "02":
			data["impuesto_id"] = 5

		#data["tipo_operacion"] = 1 if tp_op == "01" else 2

		# Validacion de los products
		if ("lines" not in data) or (type(data["lines"]) != list) or (len(data["lines"]) == 0):
			return "Se espera un array (lines) con items."
		for i, line in enumerate(data['lines']):
			if "id" not in line or type(line['id']) != int:
				return "lines[" + str(i) + "], se espera un id de producto valido."
			prod = http.request.env['product.product'].search([['id', '=', line['id']]])
			if not prod:
				return "lines[" + str(i) + "], producto no encontrado."

			#cat=http.request.env['product.category'].search([['id','=',prod.categ_id]])
			cat=prod.categ_id
			data['lines'][i] = {
				"id": line['id'],
				"descripcion": line['descripcion'] if 'descripcion' in line else prod.name,
				"precio": round(float(line['precio']), 2) if 'precio' in line else prod.lst_price,
				"descuento": round(float(line['descuento']), 2) if 'descuento' in line else 0,
				"cantidad": int(line['cantidad']) if 'cantidad' in line else 1,
				"account_id": cat.property_account_income_categ_id.id,
				"account_gasto_id": cat.property_account_expense_categ_id.id,
				"uom_id": prod.uom_id.id
			}

		# Validacion de pago
		if "pago" not in data or type(data['pago']) != dict:
			return "Se espera un parametro de pago de tido diccionario"
		pago = data['pago']
		if "monto" not in pago:
			return "Falta monto en pago["+str(i)+"]."
		if type(pago['monto']) not in [float, int]:
			return "Monto de pago invalido en pago["+str(i)+"]."

		if "detalle" not in pago:
			pago['detalle'] = " "

		if "id_transaccion" not in pago:
			pago['id_transaccion'] = ' '
		pago['id_transaccion'] = str(pago['id_transaccion'])

		if "procedencia" not in pago:
			pago['procedencia'] = 'culqi'

	@http.route('/api/factura/create', auth='public', type="json")
	def list(self, data=None):
		validation_result = self._request_validation(data)
		if validation_result is not None:
			return {
				"success": False,
				"error": validation_result
			}

		fact = False
		if data['pago']['procedencia'] == 'culqi':
			fact = http.request.env['account.invoice'].create({
				"partner_id": data['cliente_id'],
				"journal_id": data['journal_id'],
				"partner_shipping_id": data['cliente_id'],
				"date_invoice": time.strftime("%Y-%m-%d"),
				"user_id": http.request.uid,
				# team_id
				"currency_id": data['moneda'],
				"account_id": 30, # Cuentas por cobrar
				"company_id": 1, # Grupo creex
				"date_due": time.strftime("%Y-%m-%d"),
				"documentoXML": " ",
				"tipo_operacion":data["tipo_operacion"],
				"invoice_line_ids": [[0, False, {
					"discount": x['descuento'],
					"price_unit": x['precio'],
					"quantity": x['cantidad'],
					"product_id": x['id'],
					"name": x['descripcion'],
					"invoice_tax_line_ids":(6,0,[data["impuesto_id"]]),
					#"tipo_afectacion_igv": data['tipo_afectacion_igv'],
					"uom_id": x['uom_id'],
					"account_id": x['account_id'],
					"analytic_tag_ids": []
				}] for x in data['lines']]
			})
			#fact.action_invoice_open()

		pago = data['pago']
		my_pago = http.request.env['account.payment'].create({
			"payment_type": "inbound",
			"partner_type": "customer",
			"partner_id": data['cliente_id'],
			"journal_id": 11, # Diario de pago
			"amount": pago['monto'],
			"payment_date": time.strftime("%Y-%m-%d"),
			"communication": fact.move_id.name if fact else data['pago']['procedencia'],
			"currency_id": data['moneda'],
			"detalle": json.dumps(pago['detalle']),
			"payment_method_id": 1,
			"id_transaccion": pago['id_transaccion'],
			"procedencia": data['pago']['procedencia']
		})
		my_pago.post()

		return {
			"success:": True
		}
