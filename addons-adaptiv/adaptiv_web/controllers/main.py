import functools
import base64
from io import BytesIO
from PIL import Image

import odoo
from odoo import http
from odoo.modules import get_resource_path
from odoo.http import request
from odoo.addons.web.controllers.main import Binary as _Binary


IMAGE_FORMATS = ['svg', 'png']


class Binary(_Binary):

    def _logo(self, company=None, img='logo', fmt=None, **kwargs):
        if fmt and fmt not in IMAGE_FORMATS:
            raise ValueError(fmt)

        placeholder = functools.partial(get_resource_path, 'adaptiv_web', 'static', 'src', 'img')
        ResCompany = request.env['res.company']

        if company:
            try:
                company = int(company)
            except ValueError:
                company = None
            else:
                company = ResCompany.browse([company]).exists()

        if not company:
            company = ResCompany.get_current()

        for try_fmt in [fmt] if fmt else IMAGE_FORMATS:
            field = '%s_%s' % (try_fmt, img)
            values = company.read([field, 'write_date'])[0]
            if values[field]:
                image = BytesIO(base64.b64decode(values[field]))
                return http.send_file(image, filename='%s.%s' % (img, try_fmt), mtime=values['write_date'])

        return http.send_file(placeholder('%s.%s' % (img, fmt or IMAGE_FORMATS[0])))

    @http.route([
        '/web/binary/company_logo'
    ], type='http', auth='none', cors='*')
    def company_logo(self, **kwargs):
        return self._logo(**kwargs)

    @http.route([
        '/web/binary/logo',
        '/logo'
    ], type='http', auth='none', cors='*')
    def logo(self, **kwargs):
        return self._logo(**kwargs)

    @http.route([
        '/web/binary/logo_inverse',
        '/logo_inverse'
    ], type='http', auth='none', cors='*')
    def logo_inverse(self, **kwargs):
        return self._logo(img='logo_inverse', **kwargs)

    @http.route([
        '/logo.png'
    ], type='http', auth='none', cors='*')
    def logo_png(self, **kwargs):
        return self._logo(fmt='png', **kwargs)
