# -*- coding: utf-8 -*-

import json
import logging
import werkzeug
import datetime
import culqipy

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class CulqiController(http.Controller):
    _pay_url = '/payment/culqi/pago/'
    _notify_url = '/payment/paypal/ipn/'
    _return_url = '/payment/paypal/dpn/'
    _cancel_url = '/payment/paypal/cancel/'

    def payment_culqi_validate(self, transaction_id=None, sale_order_id=None):
        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return False, '/shop'

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done', 'authorized']:
            if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
                order.with_context(send_email=True).action_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return False, '/shop'

        return True, ''

    @http.route('/payment/culqi/pago/', auth='public', website=True, csrf=False)
    def culqi_pago(self, **post):
        #print post
        partner_id = request.env['res.partner'].sudo().search([['id', '=', post.get('partner_id')]])
        res = request.env['payment.transaction'].sudo().form_feedback(post, 'culqi')
        custom = json.loads(post.get('custom'))
        return http.request.render('payment_culqi.culqi_form_pay',{'order': res.sale_order_id,
                                                                   'moneda': post.get('currency_code'),
                                                                   'name_pago': 'Prueba',
                                                                   'description_pago': res.reference,
                                                                   'monto': post.get('amount'),
                                                                   'name_partner': partner_id.name,
                                                                   'public_key': post.get('pk'),
                                                                   'token': res.culqi_txn_token,
                                                                   'id_payment': res.id,
                                                                   'action_url': '/payment/culqi/pagar',
                                                                   'redirect_url': '/shop/confirmation',
                                                                   })

    @http.route('/payment/culqi/pagar', auth='public', type="http", website=True, csrf=False)
    def pagoculqui(self, **post):
        culqi = request.env["payment.acquirer"].sudo().search([["provider", "=", 'culqi']])
        pago = request.env["payment.transaction"].sudo().search([["id", "=", post.get("payment_id")]])
        culqipy.public_key = culqi.culqi_public_key if culqi.environment == 'prod' else culqi.culqi_public_key_test
        culqipy.secret_key = culqi.culqi_private_key  if culqi.environment == 'prod' else culqi.culqi_private_key_test
        charge = culqipy.Charge.create({
            "amount": int(pago.amount*100),
            "country_code": "PE",
            "currency_code": pago.currency_id.name,
            "email": pago.partner_id.email,
            "first_name": pago.partner_id.name,
            "description": pago.reference,
            "phone_number": pago.partner_id.phone,
            "source_id": post.get("token_id")
        })
        pago.culqi_txn_type = str(datetime.datetime.now()) + "\n" + json.dumps(charge)
        if charge["object"] == "charge":
            if charge["outcome"]["type"] == "venta_exitosa":
                pago.state = "done"
                pago.fees = float(charge["total_fee"])/100
                pago.date_validate = datetime.datetime.now()
                # return http.request.render("fs_payment.pago_exitoso", {})
                if pago.sale_order_id.action_confirm():
                    res, url = self.payment_culqi_validate()
                    if res:
                        return request.make_response(
                            json.dumps({'code_response': 0, 'msg_response': 'Exito'}))
                    else:
                        return request.redirect(url)
                else:
                    return request.make_response(
                        json.dumps({'code_response': -1, 'msg_response': 'Error al confirmar la orden de venta'}))

        elif charge["object"] == "error":
            pago.state = "error"
            return request.make_response(
                json.dumps({'code_response': 1, 'msg_response': charge["user_message"]}))

    @http.route('/payment/culqi/test', auth='public', website=True, csrf=False)
    def test(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            return request.render("payment_culqi.test", {'order': order,
                                                         'moneda': order.currency_id.name,
                                                           'name_pago': 'Prueba',
                                                           'description_pago':  order.payment_tx_id.reference,
                                                           'monto':  order.amount_total,
                                                           'name_partner': order.partner_id.name,
                                                           'public_key': order.payment_acquirer_id.culqi_public_key_test,
                                                           'token': order.payment_tx_id.culqi_txn_token,
                                                            'id_payment': order.payment_tx_id.id,
                                                            'return_url': '/shop',
                                                         'url_action': '/payment/culqi/test2'})
        else:
            return request.redirect('/shop')

    @http.route('/payment/culqi/test2', auth='public', type='http', website=True, csrf=False)
    def test_2(self, **post):
        return request.make_response(json.dumps({'code_response':1, 'msg_response': 'Error en Tarjeta'}))
