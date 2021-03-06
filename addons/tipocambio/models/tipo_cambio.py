import odoo
import requests
from odoo import api, models, fields
from datetime import date
import datetime
from odoo.exceptions import ValidationError, UserError

class Tipocambio(models.Model):
    _inherit = "res.currency.rate"

    fecha= fields.Date("Fecha")
    cambio_compra = fields.Float("Compra", digits=(1, 3))
    cambio_venta = fields.Float("Venta",digits=(1,3))

    """
    def actualizar_ratio_compra_venta(self):

        url = "http://www.sunat.gob.pe/a/txt/tipoCambio.txt"
        r = requests.get(url)
        if r.ok:
            valores = r.text.split('|')
            self.fecha = self.name[0:10]
           # self.fecha=valores[0][6:10]+"-"+ valores[0][3:5]+"-"+valores[0][0:2]
            self.cambio_compra = float(valores[1])
            self.cambio_venta = float(valores[2])
    """

    def actualizar_ratio_compra_venta(self):
        currency_usd = self.env['res.currency'].search([['name','=','USD']])
        url = "http://www.sunat.gob.pe/a/txt/tipoCambio.txt"
        try:
            r = requests.get(url)
            if r.ok:
                valores = r.text.split('|')
                tipo_cambio = float(valores[2])
                tipo_cambio = 1/tipo_cambio if tipo_cambio!=0.0 else 0.0
                return self.env['res.currency.rate'].create({
                    'name' : fields.Datetime.now(),
                    'currency_id': currency_usd.id,
                    'rate': tipo_cambio,
                    'fecha' : date.today(),
                    'cambio_compra' : float(valores[1]),
                    'cambio_venta' : float(valores[2])
                })
        except Exception as e:
            pass

class invoice(models.Model):
    _inherit = "account.invoice"

    tipo_cambio = fields.Float("T/C", digits=(1, 3))

    @api.constrains('tipo_cambio')
    def _check_tipo_cambio(self):
        for record in self:
            if record.tipo_cambio<=0:
                raise ValidationError("Valor del tipo de Cambio incorrecto")                
    

    @api.onchange('date_invoice')
    def get_ratio(self):
        if self.date_invoice:
            rate=self.env['res.currency.rate'].search([('fecha',"=",self.date_invoice)])
            if rate.exists():
                if self.type == "in_invoice" or self.type == "in_refund":
                    self.tipo_cambio= rate[0].cambio_venta

                if self.type == "out_invoice" or self.type == "out_refund":
                    self.tipo_cambio= rate[0].cambio_compra
            else:
                if not self.tipo_cambio:
                    self.tipo_cambio == 0


