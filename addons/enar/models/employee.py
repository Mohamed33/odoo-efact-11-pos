from openerp import fields, models, api

class Kcwebsite(models.Model):
    _inherit = 'website'

    def get_employee(self):
        return self.env['hr.employee'].search([], order='create_date asc')