# coding: utf-8

import json
import logging
from urllib.parse import urljoin
import hashlib
import random

import dateutil.parser
import pytz

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_paypal.controllers.main import PaypalController
from odoo.tools.float_utils import float_compare


_logger = logging.getLogger(__name__)


class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('culqi', 'Culqi')])

    culqi_email = fields.Char('Culqi Email', required_if_provider='culqi', groups='base.group_user')
    culqi_public_key = fields.Char('Culqi Public Key', groups='base.group_user')
    culqi_private_key = fields.Char('Culqi Private Key', groups='base.group_user')
    culqi_public_key_test = fields.Char('Culqi Public Key Test', groups='base.group_user')
    culqi_private_key_test = fields.Char('Culqi Private Key Test', groups='base.group_user')


    def _get_public_key(self):
        if self.environment == 'prod':
            return self.culqi_public_key
        else:
            return self.culqi_public_key_test

    @api.multi
    def culqi_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        culqi_tx_values = dict(values)
        culqi_tx_values.update({
            'pk' : self._get_public_key(),
            'item_name': '%s: %s' % (self.company_id.name, values['reference']),
            'item_number': values['reference'],
            'amount': values['amount'],
            'currency_code': values['currency'] and values['currency'].name or '',
            'address1': values.get('partner_address'),
            'city': values.get('partner_city'),
            'country': values.get('partner_country') and values.get('partner_country').code or '',
            'state': values.get('partner_state') and (
                        values.get('partner_state').code or values.get('partner_state').name) or '',
            'email': values.get('partner_email'),
            'zip_code': values.get('partner_zip'),
            'first_name': values.get('partner_first_name'),
            'last_name': values.get('partner_last_name'),
            'partner_id': values.get('partner_id'),
            #'paypal_return': '%s' % urlparse.urljoin(base_url, PaypalController._return_url),
            #'notify_url': '%s' % urlparse.urljoin(base_url, PaypalController._notify_url),
            #'cancel_return': '%s' % urlparse.urljoin(base_url, PaypalController._cancel_url),
            #'handling': '%.2f' % culqi_tx_values.pop('fees', 0.0) if self.fees_active else False,
            'custom': json.dumps({'return_url': '%s' % culqi_tx_values.pop('return_url')}) if culqi_tx_values.get(
                'return_url') else False,
        })
        return culqi_tx_values

    @api.multi
    def culqi_get_form_action_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return urljoin(base_url, '/payment/culqi/pago/')


class TxCulqi(models.Model):
    _inherit = 'payment.transaction'

    culqi_txn_type = fields.Char('Transaction type')

    @api.one
    def _default_token(self):
        return self._generate_token(64)

    culqi_txn_token = fields.Char("Token", states={"Borrador": [('readonly', False)]}, default=_default_token)

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------


    @api.model
    def _culqi_form_get_tx_from_data(self, data):
        #reference, txn_id = data.get('item_number'), data.get('txn_id')
        reference = data.get('item_number')
        if not reference:#or not txn_id:
            #error_msg = _('Culqi: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            error_msg = _('Culqi: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Culqi: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _generate_token(self,length=12):
        chars = list(
            'ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwyz01234567890'
        )
        random.shuffle(chars)
        chars = ''.join(chars)
        sha1 = hashlib.sha1(chars.encode('utf8'))
        token = sha1.hexdigest()
        return token[:length]

    @api.multi
    def _culqi_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _culqi_form_validate(self, data):
        status = data.get('payment_status')
        res = {
            'status': 'pending',
            'culqi_txn_type': data.get('payment_type'),
        }
        self.write(res)
        return self
        '''
        if status in ['Completed', 'Processed']:
            _logger.info('Validated Culqi payment for tx %s: set as done' % (self.reference))
            date_validate = fields.Datetime.now()
            res.update(state='done', date_validate=date_validate)
            return self.write(res)
        elif status in ['Pending', 'Expired']:
            _logger.info('Received notification for Culqi payment %s: set as pending' % (self.reference))
            res.update(state='pending', state_message=data.get('pending_reason', ''))
            return self.write(res)
        else:
            error = 'Received unrecognized status for Culqi payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)
        '''
