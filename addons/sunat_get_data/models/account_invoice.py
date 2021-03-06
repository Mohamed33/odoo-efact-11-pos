from odoo import fields,models,api 

class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    numero_documento = fields.Char(string = "Número de documento",
                                    related="partner_id.vat")
    estado_contribuyente = fields.Selection(selection=[('activo', 'Activo'), ('noactivo', 'No Activo')], 
                                            string='Estado del Contribuyente',
                                            related="partner_id.estado_contribuyente")

    def _list_tipo_documento_sunat(self):
        tipo_documento_objs = self.env["einvoice.catalog.06"].sudo().search([])
        tipo_documento_list = [(td.code,td.name) for td in tipo_documento_objs]
        return tipo_documento_list

    tipo_documento_sunat = fields.Selection(string='Tipo Doc.',
                                            selection="_list_tipo_documento_sunat", 
                                            related="partner_id.tipo_documento")                                    
    
    direccion_completa = fields.Char(string="Dirección",related="partner_id.street")

    estado_habido = fields.Selection(selection=[('habido', 'Habido'), ('nhabido', 'No Habido')], string='Estado',related="partner_id.state")