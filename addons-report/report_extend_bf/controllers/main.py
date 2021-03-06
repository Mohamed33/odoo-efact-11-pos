# -*- encoding: utf-8 -*-
import json
from base64 import standard_b64decode
import tempfile

import io
import zipfile
from py3o.template import Template
from subprocess import Popen, PIPE
from werkzeug.datastructures import Headers
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import time
from odoo.tools.safe_eval import safe_eval

from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from odoo import http
from odoo.tools.misc import find_in_path
from odoo.addons.web.controllers.main import ReportController as RC
from ._py3o_parser_context import Py3oParserContext

import logging
import sys
from imp import reload

_logger = logging.getLogger(__name__)

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")

MIME_DICT = {
    "odt": "application/vnd.oasis.opendocument.text",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "rtf": "application/rtf",
    "zip": "application/zip"
}


def compile_file(cmd):
    try:
        compiler = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    except Exception:
        msg = "Could not execute command %r" % cmd[0]
        _logger.error(msg)
        return ''
    result = compiler.communicate()
    if compiler.returncode:
        error = result
        _logger.warning(error)
        return ''
    return result[0]


def get_command(format_out, file_convert):
    try:
        unoconv = find_in_path('unoconv')
    except IOError:
        unoconv = 'unoconv'
    return [unoconv, "--stdout", "-f", "%s" % format_out, "%s" % file_convert]


def make_response(mimetype, content, file_name, out_format_file):
    headers = [
        ('Content-Type', mimetype),
        ('Content-Length', len(content)),
        ('Content-Disposition', content_disposition("%s.%s" % (file_name, out_format_file)))
    ]
    return request.make_response(content, headers=headers)


class ReportControllerExtend(RC):
    @http.route()
    def report_download(self, data, token):
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        try:
            if type == 'controller':
                reqheaders = Headers(request.httprequest.headers)
                response = Client(request.httprequest.app, BaseResponse).get(url, headers=reqheaders, follow_redirects=True)
                response.set_cookie('fileToken', token)
                return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
        return super(ReportControllerExtend, self).report_download(data, token)


class ReportController(http.Controller):

    @http.route('/report/download_document/<reportname>/<docids>', type='http', auth="user")
    @serialize_exception
    def download_document(self, **kw):
        docids = [int(i) for i in kw.get("docids").split(',')]
        t_report_name = kw.get("reportname")
        print(dir(request.env))

        Report = request.env['ir.actions.report']

        conditions = [
            ('report_type', 'in', ['controller']),
            ('report_name', '=', t_report_name)]

        report_ids = Report.search(conditions)

        assert report_ids, 'Not found report name ' + t_report_name

        particularreport_obj = report_ids[0]
        assert particularreport_obj.template_id, "Report %s not template file." % t_report_name

        report_obj = request.env[particularreport_obj.model]
        output_file = particularreport_obj.output_file
        docs = report_obj.browse(docids)
        report_name = particularreport_obj.name
        zip_filename = report_name
        if particularreport_obj.print_report_name and not len(docs) > 1:
            report_name = safe_eval(particularreport_obj.print_report_name, {'object': docs, 'time': time})
        in_stream = io.BytesIO(standard_b64decode(particularreport_obj.template_id.datas))
        #in_stream = odoo.modules.get_module_resource('report_extend_bf','templates', "test.odt")
        temp = tempfile.NamedTemporaryFile()

        if len(docids) == 1:
            print("SIiiiiiiiiiiiiiiiiiiiiiiii")
            data = dict(o=docs)
            # The custom_report method must return a dictionary
            # If any model has method custom_report
            if hasattr(report_obj, 'custom_report'):
                data.update({"data": docs.custom_report()})
            context = Py3oParserContext(request.env).localcontext
            print("context", context)
            data.update(context)
            print("data", data)

            t = Template(in_stream, temp, escape_false=True)
            t.render(data)
            temp.seek(0)
            default_out_odt = temp.read()
            if not output_file:
                temp.close()
                return make_response(MIME_DICT["odt"], default_out_odt, report_name, "odt")
            out = compile_file(get_command(output_file, temp.name))
            temp.close()
            if not out:
                return make_response(MIME_DICT["odt"], default_out_odt, report_name, "odt")
            return make_response(MIME_DICT[output_file], out, report_name, output_file)
        # if more than one zip returns
        else:
            # This is where my zip will be written
            buff = io.BytesIO()
            # This is my zip file
            zip_archive = zipfile.ZipFile(buff, mode='w')

            for doc in docs:
                data = dict(o=doc)
                if particularreport_obj.print_report_name:
                    report_name = safe_eval(particularreport_obj.print_report_name, {'object': doc, 'time': time})
                # The custom_report method must return a dictionary
                # If any model has method custom_report
                if hasattr(report_obj, 'custom_report'):
                    data.update({"data": doc.custom_report()})

                t = Template(in_stream, temp)
                t.render(data)
                temp.seek(0)
                default_out_odt = temp.read()
                if not output_file:
                    zip_archive.writestr("%s.odt" % (report_name), default_out_odt)
                else:
                    out = compile_file(get_command(output_file, temp.name))
                    if not out:
                        zip_archive.writestr("%s.odt" % (report_name), default_out_odt)
                    else:
                        zip_archive.writestr("%s.%s" % (report_name, output_file), out)
            temp.close()
            # You can visualize the structure of the zip with this command
            # print zip_archive.printdir()
            zip_archive.close()
            return make_response(MIME_DICT["zip"], buff.getvalue(), zip_filename, "zip")
