from openerp import models, fields, api, tools, _
from datetime import datetime, timedelta
import time
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_rounding = fields.Boolean("Rounding Total")
    rounding_options = fields.Selection([("digits", 'Digits'), ('points','Points'),], string='Rounding Options', default='digits')
    rounding_journal_id = fields.Many2one('account.journal',"Rounding Payment Method")

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _order_fields(self,ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'is_rounding':          ui_order.get('is_rounding') or False,
            'rounding_option':      ui_order.get('rounding_option') or False,
            'rounding':             ui_order.get('rounding') or False,
        })
        return res

    def create(self, values):
        order_id = super(PosOrder, self).create(values)
        rounding_journal_id = order_id.session_id.config_id.rounding_journal_id
        if order_id.rounding != 0:
            if rounding_journal_id:
                order_id.add_payment({
                    'amount':order_id.rounding * -1,
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('Rounding'),
                    'journal': rounding_journal_id.id,
                })
        return order_id

# POS Reorder start here
    @api.model
    def ac_pos_search_read(self, domain):
        domain = domain.get('domain')
        search_vals = self.search_read(domain)
        user_id = self.env['res.users'].browse(self._uid)
        tz = False
        result = []
        if self._context and self._context.get('tz'):
            tz = timezone(self._context.get('tz'))
        elif user_id and user_id.tz:
            tz = timezone(user_id.tz)
        if tz:
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            for val in search_vals:
                if sign == '-':
                    val.update({
                        'date_order':(datetime.strptime(val.get('date_order'), '%Y-%m-%d %H:%M:%S') - timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                elif sign == '+':
                    val.update({
                        'date_order':(datetime.strptime(val.get('date_order'), '%Y-%m-%d %H:%M:%S') + timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                result.append(val)
            return result
        else:
            return search_vals
# POS Reorder end here

    is_rounding = fields.Boolean("Is Rounding")
    rounding_option = fields.Char("Rounding Option")
    rounding = fields.Float(string='Rounding', digits=0)