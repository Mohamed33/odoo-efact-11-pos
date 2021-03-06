# -*- coding: utf-8 -*-

from odoo import models, fields, api
import boto3
import re
from odoo.exceptions import UserError


class SmsConfig(models.Model):
    _inherit = 'res.company'

    aws_sns_apikey = fields.Char(string="Api Key")
    aws_sns_apisecret = fields.Char(string="Api Secret")
    aws_sns_region = fields.Char(string="AWS Region", default="us-east-1")
    aws_sns_test_number = fields.Char(string="Test number")
    aws_sns_test_message = fields.Char(string="Test message", default="Hello world!!")
    aws_sns_log_enabled = fields.Boolean(string="Habilitar log", default=True)
    aws_sns_log_ids = fields.One2many("aws_sns_sms.sms_log", "company_id", string="Mensajes enviados")

    def send_sms(self, phonenumber, message, multiple_mensajes=False):
        if None in [self.aws_sns_apikey, self.aws_sns_apisecret]:
            raise UserError("Configurar las credenciales AWS-SNS en Company.")
        if not phonenumber or not re.match('^[+]51\\d{9}$', phonenumber):
            raise UserError("Número de celular invalido.")
        if len(message) > 140 and not multiple_mensajes:
            raise UserError("Mensaje muy largo par 1 solo sms, habilita multiple_mensajes=True si deseas enviar en varios sms.")

        client = boto3.client(
            "sns",
            aws_access_key_id=self.aws_sns_apikey,
            aws_secret_access_key=self.aws_sns_apisecret,
            region_name=self.aws_sns_region
        )
        try:
            client.publish(
                PhoneNumber=phonenumber,
                Message=message
            )
        except Exception as e:
            raise UserError(str(e))

        if self.aws_sns_log_enabled:
            self.env['aws_sns_sms.sms_log'].create({
                'phonenumber': phonenumber,
                'message': message,
                'state': 'Enviado',
                'company_id': self.id
            })

    def send_test_message(self):
        self.send_sms(self.aws_sns_test_number, self.aws_sns_test_message)


class SmsLog(models.Model):
    _name = "aws_sns_sms.sms_log"

    phonenumber = fields.Char(string="Numero")
    message = fields.Char(string="Mensaje")
    state = fields.Char(string="Estado")
    company_id = fields.Many2one("res.company", string="Company", required=True)
    partner_id = fields.Many2one("res.partner",string="Cliente")