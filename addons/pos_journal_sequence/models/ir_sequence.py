# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class IrSequence(models.Model):
    _inherit = 'ir.sequence'
    
    interpolated_prefix = fields.Char("Interpolated Prefix", compute="compute_prefix_suffix")
    interpolated_suffix = fields.Char("Interpolated Suffix", compute="compute_prefix_suffix")
    all_number_increment = fields.Integer("Number Increment", compute="compute_prefix_suffix")
    
    def _get_prefix_suffix_char(self):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if self._context.get('ir_sequence_date'):
                effective_date = datetime.strptime(self._context.get('ir_sequence_date'), '%Y-%m-%d')
            if self._context.get('ir_sequence_date_range'):
                range_date = datetime.strptime(self._context.get('ir_sequence_date_range'), '%Y-%m-%d')

            sequences = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key in sequences.keys():
                format=sequences[key]
                res[key] = effective_date.strftime(format)
                res['range_' + key] = range_date.strftime(format)
                res['current_' + key] = now.strftime(format)

            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % (self.get('name')))
        return interpolated_prefix, interpolated_suffix
    
    @api.multi
    def compute_prefix_suffix(self):
        for sequence in self:
            interpolated_prefix, interpolated_suffix = sequence._get_prefix_suffix_char()
            sequence.interpolated_prefix = interpolated_prefix
            sequence.interpolated_suffix = interpolated_suffix
            if not sequence.use_date_range:
                sequence.all_number_increment = sequence.number_next_actual
            else:
                dt = fields.Date.today()
                seq_date = sequence.env['ir.sequence.date_range'].search([('sequence_id', '=', sequence.id), ('date_from', '<=', dt), ('date_to', '>=', dt)], limit=1)
                if not seq_date:
                    seq_date = sequence._create_date_range_seq(dt)
                sequence.all_number_increment = seq_date.number_next_actual
            
    
    @api.one
    def pos_next(self, number_next_actual):
        if not self.use_date_range and self.number_next_actual<number_next_actual:
            self.sudo().number_next_actual = number_next_actual
        elif self.all_number_increment<number_next_actual:
            dt = fields.Date.today()
            seq_date = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id), ('date_from', '<=', dt), ('date_to', '>=', dt)], limit=1)
            if not seq_date:
                seq_date = self.sudo()._create_date_range_seq(dt)
            seq_date.sudo().number_next_actual = number_next_actual
