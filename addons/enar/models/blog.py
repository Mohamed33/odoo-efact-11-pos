from openerp import fields, models, api

class Kcwebsiteblog(models.Model):
    _inherit = 'website'

    def get_blog_post(self):
        return self.env['blog.post'].search([], order='create_date desc', limit=3)