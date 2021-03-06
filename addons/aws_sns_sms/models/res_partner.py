from odoo import models,api,fields 

class VistaEnviarMensaje(models.TransientModel):
    _name = "vista.enviarmensaje"
    mensaje = fields.Char("Mensaje")
    celular = fields.Char("Celular")
    company_id = fields.Many2one("res.company")
    partner_id = fields.Many2one("res.partner",string="Cliente")
        
    """
    def _default_company(self):
        company_id = self.env['res.company']._company_default_get('aws_sns_sms')
        return company_id
    """
    def btn_enviar_mensaje(self):
        phonenumber = self.celular
        message = self.mensaje
        multiple_mensajes = True
        try:
            self.company_id.send_sms(phonenumber,message,multiple_mensajes)
            self.env['aws_sns_sms.sms_log'].create({
                    'phonenumber': phonenumber,
                    'message': message,
                    'state': 'Enviado',
                    'company_id': self.company_id.id,
                    'partner_id':self.partner_id.id
                })
        except Exception as e:
            self.env['aws_sns_sms.sms_log'].create({
                    'phonenumber': phonenumber,
                    'message': message,
                    'state': e,
                    'company_id': self.company_id.id,
                    'partner_id':self.partner_id.id
                })
    


class ResPartner(models.Model):
    _inherit = 'res.partner'
    msg_ids = fields.One2many("aws_sns_sms.sms_log","partner_id",string="Mensajes")


    def btn_vista_envio_mensaje(self):
        view_id = self.env.ref("aws_sns_sms.view_form_enviar_mensaje").id
        return {
            "type":"ir.actions.act_window",
            "views":[(view_id,"form")],
            "res_model":"vista.enviarmensaje",
            "target":"new",
            "context":{
                "default_partner_id":self.id,
                "default_celular":self.mobile,
                "default_company_id":self.company_id.id
            }
        }
    