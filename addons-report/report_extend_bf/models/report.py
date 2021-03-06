# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from base64 import standard_b64decode
import tempfile
import io
import zipfile
from py3o.template import Template
from subprocess import Popen, PIPE
import time

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import find_in_path

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


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    report_type = fields.Selection(
        selection_add=[('controller', 'Controller')])
    template_id = fields.Many2one("ir.attachment", "Template *.odt")
    output_file = fields.Selection(
        (("pdf", "pdf"),
         ("ods", "ods"),
         ("doc", "doc"),
         ("rtf", "rtf"),
         ("docx", "docx")),
        string="Format Output File.",
        help='Format Output File. (Format Default *.odt Output File)'
    )

    @api.multi
    def render_any_docs(self, res_ids=None, data=None):
        if not data:
            data = {}
        docids = res_ids

        report_obj = self.env[self.model]
        output_file = self.output_file
        docs = report_obj.browse(docids)
        report_name = self.name
        zip_filename = report_name
        if self.print_report_name and not len(docs) > 1:
            report_name = safe_eval(self.print_report_name, {'object': docs, 'time': time})
        in_stream = io.BytesIO(standard_b64decode(self.template_id.datas))
        #in_stream = odoo.modules.get_module_resource('report_extend_bf','templates', "test.odt")
        temp = tempfile.NamedTemporaryFile()

        if len(docids) == 1:
            data = dict(o=docs)
            # The custom_report method must return a dictionary
            # If any model has method custom_report
            if hasattr(report_obj, 'custom_report'):
                data.update({"data": docs.custom_report()})

            t = Template(in_stream, temp)
            t.render(data)
            temp.seek(0)
            default_out_odt = temp.read()
            if not output_file:
                temp.close()
                return MIME_DICT["odt"], default_out_odt, report_name, "odt"
            out = compile_file(get_command(output_file, temp.name))
            temp.close()
            if not out:
                return MIME_DICT["odt"], default_out_odt, report_name, "odt"
            return MIME_DICT[output_file], out, report_name, output_file
        # if more than one zip returns
        else:
            # This is where my zip will be written
            buff = io.BytesIO()
            # This is my zip file
            zip_archive = zipfile.ZipFile(buff, mode='w')

            for doc in docs:
                data = dict(o=doc)
                if self.print_report_name:
                    report_name = safe_eval(self.print_report_name, {'object': doc, 'time': time})
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
            return MIME_DICT["zip"], buff.getvalue(), zip_filename, "zip"
