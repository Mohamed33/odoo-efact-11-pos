from odoo import models,api,fields 

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    group_multi_currency = fields.Boolean(group='base.group_user',default=True)



    