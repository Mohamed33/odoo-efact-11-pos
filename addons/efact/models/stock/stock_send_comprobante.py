
from odoo import models, fields, api, exceptions
import re
import datetime
import json
from ..auth import oauth


class StockPinkingType(models.Model):
    _inherit = "stock.picking.type"

    is_with_guia = fields.Boolean(string="Es con Guia de Remision?", default=False)


class StockSendComprobante(models.Model):
    _inherit = "stock.picking"

    is_guia_picking = fields.Boolean(string="Es guia?", related='picking_type_id.is_with_guia')
    motivo_traslado = fields.Selection(string="Motivo de Traslado", default="01",
                                       selection=[('01', 'VENTA'),
                                                  ('14', 'VENTA SUJETA A CONFIRMACION DEL COMPRADOR'),
                                                  ('02', 'COMPRA'),
                                                  ('04', 'TRASLADO ENTRE ESTABLECIMIENTOS DE LA MISMA EMPRESA'),
                                                  ('18', 'TRASLADO EMISOR ITINERANTE CP'),
                                                  ('08', 'IMPORTACION'),
                                                  ('09', 'EXPORTACION'),
                                                  ('19', 'TRASLADO A ZONA PRIMARIA'),
                                                  ('13', 'OTROS')])
    desc_motivo_traslado = fields.Char(string="Descripcion Motivo Traslado", default="")
    ind_trans_program = fields.Boolean(string="Transbordo programado?", default=False)
    peso_total = fields.Float(string="Peso total", digits=(10, 2))
    peso_unidad_medida = fields.Char(string="Unidad de medida. Catalogo Nro 3")
    numero_bultos = fields.Integer(string="Numero de bultos", default=1)
    transportes = fields.One2many("efact.stock_transporte", "picking_id", string="Transporte")
    salida_ubigeo = fields.Char(string="Salida ubigeo")
    salida_direccion = fields.Char(string="Salida direccion")

    entrega_ubigeo = fields.Char(string="Entrega Ubigeo")
    entrega_direccion = fields.Char(string="Engrega Direccion")
    # falta contenedor y puerto

    estado_envio = fields.Selection(string="Estado de envio",
                                    default=0,
                                    selection=[(0, "Pendiente"), (1, "Enviado"), (2, "Error")])
    json_enviado = fields.Text(string="Json enviado")
    xml_generado = fields.Text(string="Xml generado")
    digest_value = fields.Char(string="Digest Value")

    def validar_datos_compania(self):
        errors = []
        if not self.company_id.partner_id.vat:
            errors.append("* No se tiene configurado el RUC de la empresa emisora")
        if not self.company_id.partner_id.tipo_documento:
            errors.append("* No se tiene configurado el tipo de documento de la empresa emisora")
        elif self.company_id.partner_id.tipo_documento != '6':
            errors.append("* El Tipo de Documento de la empresa emisora debe ser RUC")
        if not self.company_id.partner_id.zip:
            errors.append("* No se encuentra configurado el Ubigeo de la empresa emisora.")
        if not self.company_id.partner_id.street:
            errors.append("* No se encuentra configurado la dirección de la empresa emisora.")
        if not self.company_id.partner_id.registration_name:
            errors.append("* No se encuentra configurado la Razón Social de la empresa emisora.")
        return errors

    @api.multi
    def action_generar_comprobante_json(self):
        if self.estado_envio == 1:
            raise exceptions.UserError("Documento ya fue aceptado anteriormente.")

        if not self.name or not re.match('T\\d{3}-\\d{1,8}', self.name):
            raise exceptions.UserError("El codigo no tiene el formato correcto: " + str(self.name))
        errors = self.validar_datos_compania()
        if len(errors) > 0:
            raise exceptions.UserError("Error al validar datos de la compania:\n" + '\n'.join(errors))

        serie, correlativo = self.name.split('-')
        company = self.company_id.partner_id
        receptor = self.partner_id

        documento = {
            "serie": serie,
            "correlativo": int(correlativo),
            "nombreEmisor": company.name,
            "tipoDocEmisor": '6',
            "numDocEmisor": company.vat,
            "tipoDocReceptor": receptor.tipo_documento,
            "numDocReceptor": receptor.vat,
            "nombreReceptor": receptor.name,
            "motivoTraslado": self.motivo_traslado,
            "descripcionMotivoTraslado": self.desc_motivo_traslado,
            "transbordoProgramado": self.ind_trans_program,
            "pesoTotal": self.peso_total,
            "pesoUnidadMedida": self.peso_unidad_medida,
            "numeroBulltosPallets": self.numero_bultos,
            "entregaUbigeo": self.entrega_ubigeo,
            "entregaDireccion": self.entrega_direccion,
            "salidaUbigeo": self.salida_ubigeo,
            "salidaDireccion": self.salida_direccion,
        }
        transportes = []
        for t in self.transportes:
            transportes.append({
                "modoTraslado": t.modoTraslado,
                "fechaInicioTraslado": t.fechaInicioTraslado,
                "tipoDocTransportista": t.tipoDocTransportista,
                "numDocTransportista": t.numDocTransportista,
                "nombreTransportista": t.nombreTransportista,
                "placaVehiculo": t.placaVehiculo,
                "tipoDocConductor": t.tipoDocConductor,
                "numDocConductor": t.numDocConductor,
            })
        detalles = []
        for d in self.move_lines:
            detalles.append({
                'cantidadItem': d.product_uom_qty,
                'unidadMedidaItem': d.product_uom.code,
                'codItem': str(d.id),
                'nombreItem': d.name,
            })

        data = {
            "tipoDocumento": "09",
            "fechaEmision": datetime.datetime.now().strftime("%Y-%m-%d"),
            "documento": documento,
            "transportes": transportes,
            "detalle": detalles
        }
        self.json_enviado = json.dumps(data, ensure_ascii=False, indent=2)

        resp = oauth.enviar_doc_url(
            self.company_id.endpoint,
            data,
            oauth.generate_token_by_company(self.company_id),
            self.company_id.tipo_envio)

        resp = resp.json()
        if not resp['success']:
            raise exceptions.UserError("Error en la api:\n" + json.dumps(resp, ensure_ascii=False, indent=2))

        resp = resp['result']
        # print(json.dumps(resp, ensure_ascii=False, indent=2))
        if resp.get("success", False) and resp.get("sunat_status", "x") == "A":
            self.digest_value = resp["digest_value"]
            self.xml_generado = resp["signed_xml"]
            self.estado_envio = 1
        else:
            self.estado_envio = 2
            if "errors" in resp and type(resp['errors']) == str:
                msg = resp['errors']
            else:
                msg = json.dumps(resp, ensure_ascii=False, indent=2)

            raise exceptions.UserError(msg)
        return True


class StockTransporte(models.Model):
    _name = "efact.stock_transporte"

    modoTraslado = fields.Selection(string="Modalidad de traslado",
                                    selection=[("01", "Publico"), ("02", "Privado")])
    fechaInicioTraslado = fields.Date(string="Inicio del traslado")
    tipoDocTransportista = fields.Char(string="Transportista>Tipo documento")
    numDocTransportista = fields.Char(string="Transportista>Numero documento")
    nombreTransportista = fields.Char(string="Transportista>Nombre")
    placaVehiculo = fields.Char(string="Placa Vehiculo")
    tipoDocConductor = fields.Char("Conductor>Tipo documento")
    numDocConductor = fields.Char("Conductor>Numero de documento")

    picking_id = fields.Many2one("stock.picking", string="Picking", required=True)
