#!/usr/bin/env python2
import requests
from odoo.exceptions import UserError, ValidationError
import json
import os
import datetime
from bs4 import BeautifulSoup
import jwt
import time
from ..utils.number_to_letter import to_word
import re
from odoo import fields
from xml.dom.minidom import parse, parseString
from requests.exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError,
    FileModeWarning, ConnectTimeout, ReadTimeout
)
import logging 
_logger = logging.getLogger()

def generate_token_by_company(company_id, time_valid=10000):
    if not (company_id.api_key and company_id.api_secret):
        raise UserError("API Credenciales no configuradas")

    api_key = company_id.api_key
    api_secret = company_id.api_secret
    headers = {
        "iss": api_key
    }
    payload = {
        "exp": int(time.time()) + time_valid,
    }
    token = jwt.encode(payload, api_secret, 'HS256', headers)
    return token


def generate_token(api_key, api_secret, time_valid=10000):
    headers = {
        "iss": api_key
    }
    payload = {
        "exp": int(time.time()) + time_valid,
    }
    token = jwt.encode(payload, api_secret, 'HS256', headers)
    return token


def consulta_comprobante(company_id, ruc, tipo_comprobante, serie_comprobante, numero_comprobante):
    token = generate_token_by_company(company_id, 10000)
    data = {
        "method": "Factura.consultaComprobante",
        "kwargs":
        {"data": {"ruc": ruc, "tipo_comprobante": tipo_comprobante,
                  "serie_comprobante": serie_comprobante, "numero_comprobante": numero_comprobante}}
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    r = requests.post(company_id.endpoint, headers=headers,
                      data=json.dumps(data))

    return r

def consultar_validez_comprobante(company,lista_consultas):
    token = generate_token_by_company(company, 10000)
    data = {
        "method": "EFact21.consulta_validez_comprobante_v2",
        "kwargs":{
            "data": lista_consultas
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    r = requests.post(company.endpoint, headers=headers,data=json.dumps(data))
    _logger.info(r)
    if r.status_code == 200:
        return r
    else:
        raise UserError(r.text)

def consulta_estado_comprobante(URL_GRAL, request_id, api_key, api_secret):
    url = URL_GRAL
    token = generate_token(api_key, api_secret, 10000)
    data = {
        "method": "Log.get_log",
        "kwargs": {"id": request_id}
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))

    return r

def enviar_doc_baja_url(URL_GRAL, data_doc, token, tipoEnvio):
    url = URL_GRAL
    data_doc["tipoEnvio"] = int(tipoEnvio)
    data = {
        "method": "EFact21.lamdba",
        "kwargs": {"data": data_doc}
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    # os.system("echo '%s'"%(json.dumps(data)))
    r = requests.post(url, headers=headers, data=json.dumps(data))

    return r

def enviar_doc_resumen_url(URL_GRAL, data_doc, token, tipoEnvio):
    url = URL_GRAL
    data_doc["tipoEnvio"] = int(tipoEnvio)
    data = {
        "method": "EFact21.lamdba",
        "kwargs": {"data": data_doc}
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    # os.system("echo '%s'"%(json.dumps(data)))
    r = requests.post(url, headers=headers, data=json.dumps(data))

    return r


def enviar_doc_url(URL_GRAL, data_doc, token, tipoEnvio):
    url = URL_GRAL
    data_doc["tipoEnvio"] = int(tipoEnvio)
    data = {
        "method": "EFact21.lamdba",
        "kwargs": {"data": data_doc}
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=10000)

    return r


def enviar_doc(self, url):
    token = generate_token(self.company_id.api_key,
                           self.company_id.api_secret, 10000)

    self.invoice_type_code = self.journal_id.invoice_type_code_id
    if self.invoice_type_code == "01" or self.invoice_type_code == "03":
        data_doc = crear_json_fac_bol(self)
    elif self.invoice_type_code == "07" or self.invoice_type_code == "08":
        data_doc = crear_json_not_cred_deb(self)
    else:
        raise UserError("Tipo de documento no valido")      
    
    self.json_comprobante = json.dumps(data_doc, indent=4)
    data = {
        "request_json":self.json_comprobante,
        "name":self.name,
        "date_request":fields.Datetime.now(),
        "date_issue":self.date_invoice,
        "account_invoice_id":self.id
    }
    try:
        response_env = enviar_doc_url(url, data_doc, token, self.company_id.tipo_envio)
        self.json_respuesta = json.dumps(response_env.json(), indent=4)
        data.update({
            "response_json":self.json_respuesta,
        })
        if response_env.status_code == 200:
            # Envío exitoso
            response_env = response_env.json()
            if "result" in response_env:
                result = response_env["result"]
                if "sunat_status" in result:
                    if result["sunat_status"] in ["A","O","P","E","N","B"]:
                        self.estado_emision = result["sunat_status"]
                    else:
                        self.estado_emision = "P"

                if "digest_value" in result:
                    data["digest_value"] = result["digest_value"]
                    self.digest_value = result["digest_value"]

                if "signed_xml" in result:
                    try:
                        ps = parseString(result["signed_xml"])
                        data["signed_xml_data"] = ps.toprettyxml()
                    except Exception as e:
                        data["signed_xml_data"] = result["signed_xml"]
                    data["signed_xml_data_without_format"] = result["signed_xml"]

                if "response_content_xml" in result:
                    try:
                        ps = parseString(result["response_content_xml"])
                        data["content_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["content_xml"] = result["response_content_xml"]
                    
                if "response_xml" in result:
                    try:
                        ps = parseString(result["response_xml"])
                        data["response_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["response_xml"] = result["response_xml"]            
                    data["response_xml_without_format"] = result["response_xml"]
                    
                if "tipoDocumento" in data_doc:
                    tipo_documento = data_doc["tipoDocumento"]
                    if tipo_documento == '01':
                        data["name"] = "Factura electrónica "+self.number
                    elif tipo_documento == '03':
                        data["name"] = "Boleta Electrónica "+self.number
                    elif tipo_documento == '07':
                        data["name"] = "Nota de Crédito "+self.number
                    elif tipo_documento == '08':
                        data["name"] = "Nota de Débito "+self.number
                    
                if "unsigned_xml" in result:
                    try:
                        ps = parseString(result["unsigned_xml"])
                        data["unsigned_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["unsigned_xml"] = result["unsigned_xml"]

                if "sunat_status" in result:
                    data["status"] = result["sunat_status"]
                if 'request_id' in response_env['result']:
                    data["api_request_id"] = result['request_id']

    except Timeout as e:
        self.estado_emision = "P"
        return {
                'name': 'Tiempo de espera excedido',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': "Alerta",
                    'default_accion':"* El Comprobante ha sido generado de forma exitosa.\n* El tiempo de espera de la respuesta ha sido excedida.\n* El comprobante se enviará de forma automática luego"
            
                }
            }
    except ConnectionError as e:
        self.estado_emision = "P"
        return {
                'name': 'Error en la conexión',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': "Alerta",
                    'default_accion':"* El Comprobante ha sido generado de forma exitosa.\n* No se ha logrado enviar el comprobante.\n* Se intentará enviar luego de forma automática."
                }
            }
    except Exception as e:
        self.estado_emision = "P"
        return {
                'name': 'Error',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': "Alerta",
                    'default_accion':"* El Comprobante ha sido generada de forma exitosa.\n* "+str(e)
                }
            }
    finally:
        self.account_log_status_ids = [(0, 0, data)]


def baja_doc(self):
    token = generate_token(self.company_id.api_key,
                           self.company_id.api_secret, 10000)
    data_doc = crear_json_baja(self)
    response_env = enviar_doc_resumen_url(
        self.company_id.endpoint, data_doc, token, self.company_id.tipo_envio)
    self.json_comprobante = data_doc
    self.json_respuesta = json.dumps(response_env.json(), indent=4)
    if response_env.ok:
        self.status_envio = True
        self.estado_emision = extaer_estado_emision(response_env.json())
        return True, ""
    else:
        recepcionado, estado_emision, msg_error = extraer_error(response_env)
        if recepcionado:
            self.status_envio = True
            self.estado_emision = estado_emision
            return True, msg_error
        else:
            return False, msg_error


def extaer_estado_emision(response_env):
    result = response_env.get("result", False)
    if result:
        if result.get("data", False):
            data = result["data"]
            return data['estadoEmision']
    return ""

import json
def extraer_error(response_env):

    if not response_env.get("success"):
        raise UserError(json.dumps(response_env))

    if response_env.get("result",False):
        if response_env["result"].get("errors"):
            errors =response_env["result"].get("errors")
        else:
            raise UserError(json.dumps(response_env["result"]))
    else:
        raise UserError(json.dumps(response_env))

    #errors = response_env["result"]['errors']
    msg_error = ""
    i_error = 1
    estado_emision = ""
    recepcionado = False
    for error in errors:
        if 'meta' in error:
            error_meta = error['meta']
            if 'estadoEmision' in error_meta:
                estado_emision = error_meta['estadoEmision']
                recepcionado = True

            if 'codigoErrorSUNAT' in error_meta:
                msg_error = msg_error + "ERROR N " + \
                    str(i_error) + ": Error en SUNAT " + \
                    error_meta['codigoErrorSUNAT'] + \
                    error_meta['descripcionErrorSUNAT']
            else:
                # + " - " + error['detail'].encode('latin1')
                msg_error = msg_error + "ERROR N " + \
                    str(i_error) + ": " + str(error['code'])
        else:
            # + " - " + error['detail'].encode('latin1')
            msg_error = msg_error + "ERROR N " + \
                str(i_error) + ": " + str(error['code'])

        i_error = i_error + 1

    return recepcionado, estado_emision, msg_error


def get_tipo_cambio(self, compra_o_venta=2):  # 1 -> compra , 2->venta
    ratios = self.currency_id.rate_ids
    tipo_cambio = 1.0
    ratio_actual = False
    for ratio in ratios:
        if str(ratio.name)[0:10] == str(self.date_invoice):
            tipo_cambio = ratio.rate
            ratio_actual = True

    if ratio_actual:
        return tipo_cambio
    else:
        now = datetime.datetime.now()
        if self.date_invoice > now.strftime("%Y-%m-%d"):
            raise ValidationError("Fecha de factura no valida, no se puede obtener tipo de cambio de esa fecha")
        url = "https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx"
        r = requests.get(url)
        if r.ok:
            soup = BeautifulSoup(r.text, 'html.parser')
            tipo_cambio = float(soup.find(id="ctl00_cphContent_rgTipoCambio_ctl00__0").find_all('td')[compra_o_venta].string)
            self.env['res.currency.rate'].create({
                'name': now.strftime("%Y-%m-%d"),
                'currency_id': self.currency_id.id,
                'rate': tipo_cambio
            })
            return tipo_cambio
        else:
            raise ValidationError("Error al obtener tipo de cambio en SBS")


    

# CREAR TIPOS DE JSON
def crear_json_fac_bol(self):

    if self.invoice_type_code == '01':
        if not re.match("^F\w{3}-\d{1,8}$", self.number):
            raise UserError("El Formato de la Factura es incorrecto.")
    elif self.invoice_type_code == '03':
        if not re.match("^B\w{3}-\d{1,8}$", self.number):
            raise UserError("El Formato de la Boleta es Incorrecto.")
    elif self.invoice_type_code == '07':
        if self.refund_invoice_id.invoice_type_code == '01':
            if not re.match("^F\w{3}-\d{1,8}$", self.number):
                raise UserError(
                    "El Formato de la Nota de Crédito para la factura es incorrecto. ")
        if self.refund_invoice_id.invoice_type_code == '03':
            if not re.match("^B\w{3}-\d{1,8}$", self.number):
                raise UserError(
                    "El Formato de la Nota de Crédito para la Boleta es Incorrecto. ")
    elif self.invoice_type_code == '08':
        if self.refund_invoice_id.invoice_type_code == '01':
            if not re.match("^F\w{3}-\d{1,8}$", self.number):
                raise UserError(
                    "El Formato de la Nota de Débito para la factura es incorrecto. ")
        if self.refund_invoice_id.invoice_type_code == '03':
            if not re.match("^B\w{3}-\d{1,8}$", self.number):
                raise UserError(
                    "El Formato de la Nota de Débito para la Boleta es Incorrecto. ")
    else:
        raise UserError("El Tipo de Documento del Comprobante es Obligatorio")

    nombreEmisor = self.company_id.partner_id.registration_name.strip()
    numDocEmisor = self.company_id.partner_id.vat.strip() if self.company_id.partner_id.vat else ""

    numDocReceptor = self.partner_id.vat.strip() if self.partner_id.tipo_documento in ["1", "6"] and self.partner_id.vat else "-"
    nombreReceptor = self.partner_id.registration_name if self.partner_id.registration_name not in ["-",False,""," - "] else self.partner_id.name
    nombreReceptor = nombreReceptor.strip()
    tipoDocReceptor = self.partner_id.tipo_documento
    direccionReceptor =  self.partner_id.street if self.partner_id.street else "-"
    nombreComercialReceptor = replace_false(self.partner_id.name if self.partner_id.name else self.partner_id.registration_name)

    correlativo = int(self.number.split("-")[1])
    data = {
        "tipoDocumento": self.invoice_type_code,
        "fechaEmision": self.date_invoice,
        "idTransaccion": self.number,
        "correoReceptor": replace_false(self.partner_id.email if self.partner_id.email else "-"),
        "documento": {
            "serie": self.journal_id.code,
            "correlativo": correlativo,
            "nombreEmisor": nombreEmisor,
            "tipoDocEmisor": self.company_id.partner_id.tipo_documento,
            "numDocEmisor": numDocEmisor,
            "direccionReceptor": direccionReceptor,
            "direccionOrigen": replace_false(self.company_id.partner_id.street),
            "direccionUbigeo": replace_false(self.company_id.partner_id.zip),
            "nombreComercialEmisor": replace_false(self.company_id.partner_id.registration_name),
            "tipoDocReceptor": tipoDocReceptor,
            "numDocReceptor":  numDocReceptor,
            "nombreReceptor": nombreReceptor,
            "nombreComercialReceptor": replace_false(self.partner_id.name if self.partner_id.name else self.partner_id.registration_name),
            # VERIFICAR
            ##"tipoDocReceptorAsociado": replace_false(self.partner_id.tipo_documento),
            ##"numDocReceptorAsociado": self.partner_id.vat if self.partner_id.tipo_documento in ["1", "6"] and self.partner_id.vat else "-",
            ##"nombreReceptorAsociado": replace_false(self.partner_id.registration_name if self.partner_id.registration_name else self.partner_id.name),
            # "direccionDestino" : "",#solo para boletas
            "tipoMoneda": self.currency_id.name,
            # "sustento" : "", #solo notas
            # "tipoMotivoNotaModificatoria" : "", #solo_notas
            "mntNeto": round(self.total_venta_gravado, 2),
            "mntExe": round(self.total_venta_inafecto, 2),
            "mntExo": round(self.total_venta_exonerada, 2),
            "mntTotalIgv": round(self.amount_tax, 2),
            "mntTotal": round(self.amount_total, 2),
            # solo para facturas y boletas
            "mntTotalGrat": round(self.total_venta_gratuito, 2),
            "fechaVencimiento": self.date_due if self.date_due else now.strftime("%Y-%m-%d"),
            "glosaDocumento": "VENTA",  # verificar
            "codContrato": replace_false(self.number),
            # "codCentroCosto" : "",
            # verificar
            "tipoCambioDestino": round(self.tipo_cambio_fecha_factura, 4),
            "mntTotalIsc": 0.0,
            "mntTotalOtros": 0.0,
            "mntTotalOtrosCargos": 0.0,
            # "mntTotalAnticipos" : 0.0, #solo factura y boleta
            "tipoFormatoRepresentacionImpresa": "GENERAL",
            "mntTotalLetras": to_word(round(self.amount_total, 2), self.currency_id.name)
        },
        "descuento": {
            "mntDescuentoGlobal": round(self.total_descuento_global,2),
            "mntTotalDescuentos": round(self.total_descuentos,2)
        },
        # solo factura y boleta
        # "servicioHospedaje": { },
        # solo factura y boleta, con expecciones

        "indicadores": {
            # VERIFICAR ESTOS CAMPOS
            "indVentaInterna": True if self.tipo_operacion == "01" else 0,
            "indExportacion": True if self.tipo_operacion == "02" else 0,
            # "indNoDomiciliados" : False, #valido para notas
            "indAnticipo": True if self.tipo_operacion == "04" else 0,
            # "indDeduccionAnticipos" : False,
            # "indServiciosHospedaje" : False,
            "indVentaItinerante": True if self.tipo_operacion == "05" else 0
            # "indTrasladoBienesConRepresentacionImpresa" : False,
            # "indVentaArrozPilado" : False,
            # "indComprobantePercepcion" : False,
            # "indBienesTransferidosAmazonia" : False,
            # "indServiciosPrestadosAmazonia" : False,
            # "indContratosConstruccionEjecutadosAmazonia" : False

        },

        # solo factura y boleta
        # "percepcion": {
        # "mntBaseImponible" : 0.0,
        # "mntPercepcion" : 0.0,
        # "mntTotalMasPercepcion" : 0.0,
        # "tasaPercepcion" : 1.0
        # },
        # "datosAdicionales": {},
    }
    data_impuesto = []
    data_detalle = []
    data_referencia = []  # solo para notas
    data_anticipo = []  # solo facturas y boletas
    data_anexo = []  # si hay anexos

    if self.descuento_global:
        data["documento"]["descuentoGlobal"] = {
            "factor":round(self.descuento_global/100.00,2),
            "montoDescuento":round(self.total_descuento_global,2),
            "montoBase":round(self.amount_untaxed + self.total_descuento_global,2) # El atributo amount_untaxed es el monto del total de ventas sin impuestos
        }

    if self.numero_guia_remision:
        data["documento"]["numero_guia"] = self.numero_guia_remision

    if self.nota_id:
        data["nota"] = self.nota_id.descripcion

    for tax in self.tax_line_ids:
        data_impuesto.append({
            "codImpuesto": str(tax.tax_id.tax_group_id.code),
            "montoImpuesto": round(tax.amount,2),
            "tasaImpuesto": round(tax.tax_id.amount/100,2)
        })

    if len(self.tax_line_ids) == 0:
        data_impuesto.append({
            "codImpuesto": "1000",
            "montoImpuesto": 0.0,
            "tasaImpuesto": 0.18
        })

    for item in self.invoice_line_ids:
        #price_unit = item.price_unit*(1-(item.discount/100)) - item.descuento_unitario
        #descuento = item.price_unit*item.discount/100 + item.descuento_unitario
        """
        price_unit = item.price_unit
        descuento_unitario = item.descuento_unitario
        descuento = 0
        tasaIgv = item.invoice_line_tax_ids[0].amount /100 if len(item.invoice_line_tax_ids) else ""
        if (item.invoice_line_tax_ids.price_include):

            if (item.invoice_line_tax_ids.amount == 0):
                montoImpuestoUni = 0
                base_imponible = price_unit
                descuento = (base_imponible*item.discount /
                             100 + descuento_unitario)
            else:
                base_imponible = price_unit / (1+tasaIgv)
                descuento_unitario = descuento_unitario / (1+tasaIgv)
                descuento = (base_imponible*item.discount /
                             100 + descuento_unitario)
                montoImpuestoUni = price_unit - base_imponible - descuento*tasaIgv
            precioItem = price_unit
        else:
            base_imponible = price_unit
            descuento = (base_imponible*item.discount/100 + descuento_unitario)
            montoImpuestoUni = (price_unit - descuento)*tasaIgv
            precioItem = price_unit + montoImpuestoUni
            base_imponible = price_unit

        montoItem = round((base_imponible) * item.quantity, 2)
        nombreItem = item.name.strip().replace("\n","")
        """
        if item.invoice_line_tax_ids:
            taxes = item.invoice_line_tax_ids.compute_all(item.price_unit)
        precioItemSinIgv = taxes["total_excluded"]
        
        tasaIgv = item.invoice_line_tax_ids[0].amount /100 if len(item.invoice_line_tax_ids) else ""

        datac = {
            "cantidadItem": round(item.quantity, 2),
            "unidadMedidaItem": item.uom_id.code,
            "codItem": str(item.product_id.id),
            "nombreItem": item.name[0:250],
            "precioItem": round(item.price_unit, 2) if len([item  for line_tax in item.invoice_line_tax_ids 
                                                            if line_tax.tipo_afectacion_igv.code  in ["31","32","33","34","35","36"] ] )==0 else 0,#Precio unitario con IGV
            
            "precioItemSinIgv": round(precioItemSinIgv, 2) if len([item  for line_tax in item.invoice_line_tax_ids 
                                                                if line_tax.tipo_afectacion_igv.code  in ["31","32","33","34","35","36"] ] )==0 else 0,#Precio unitario sin IGV y sin descuento
            
            "montoItem": round(item.price_unit*item.quantity, 2) if item.no_onerosa else round(item.price_subtotal,2), #Monto total de la línea sin IGV
            
            #"descuentoMonto": round((item.price_subtotal*item.discount/100.0)/(1-item.discount/100.0), 2),  # solo factura y boleta
            "codAfectacionIgv": item.invoice_line_tax_ids[0].tipo_afectacion_igv.code if len(item.invoice_line_tax_ids) else "",
            "tasaIgv": round(tasaIgv*100, 2),
            "montoIgv": round(item.price_total-item.price_subtotal, 2),#Monto Total del IGV
            "codSistemaCalculoIsc": "01",  # VERIFICAR
            "montoIsc": 0.0,  # VERIFICAR
            # "tasaIsc" : 0.0, #VERIFICAR
            # VERIFICAR
            "precioItemReferencia": round(item.price_unit, 2) ,
            "idOperacion": str(self.id),
            "no_onerosa": True if item.no_onerosa else False
        }
        if item.discount:
            datac["descuento"] = {
                "factor":round(item.discount/100.0,2),
                "montoDescuento":round((item.price_subtotal*item.discount/100.0)/(1-item.discount/100.0), 2),
                "montoBase":round(item.price_subtotal/(1-item.discount/100.0),2)
            }

        data_detalle.append(datac)

    data["impuesto"] = data_impuesto
    data["detalle"] = data_detalle
    if len(data_anticipo):
        data["anticipos"] = data_anticipo
    if len(data_anexo):
        data["anexos"] = data_anexo

    return data
    # return json.dumps(data,indent=4)


def crear_json_not_cred_deb(self):
    now = fields.Datetime.now()

    nombreEmisor = self.company_id.partner_id.registration_name.strip()
    numDocEmisor = self.company_id.partner_id.vat.strip() if self.company_id.partner_id.vat else ""

    numDocReceptor = self.partner_id.vat.strip() if self.partner_id.tipo_documento in ["1", "6"] and self.partner_id.vat else "-"
    nombreReceptor = self.partner_id.registration_name if self.partner_id.registration_name not in ["","-"," - ",False] else self.partner_id.name
    nombreReceptor = nombreReceptor.strip()
    correlativo = int(self.number.split("-")[1])
    

    data = {
        "tipoDocumento": self.journal_id.invoice_type_code_id,
        "fechaEmision": self.date_invoice,
        "idTransaccion": self.number,
        "correoReceptor": replace_false(self.partner_id.email if self.partner_id.email else "-"),
        "documento": {
            "serie": self.journal_id.code,
            "correlativo": correlativo,
            "nombreEmisor": nombreEmisor,
            "tipoDocEmisor": self.company_id.partner_id.tipo_documento,
            "numDocEmisor": numDocEmisor,
            "direccionOrigen": replace_false(self.company_id.partner_id.street),
            "direccionUbigeo": replace_false(self.company_id.partner_id.zip),
            "nombreComercialEmisor": replace_false(self.company_id.partner_id.registration_name),
            "tipoDocReceptor": self.partner_id.tipo_documento,
            "numDocReceptor": numDocReceptor,
            "nombreReceptor":nombreReceptor,
            "nombreComercialReceptor": replace_false(
                self.partner_id.name if self.partner_id.name else self.partner_id.registration_name),
            "direccionReceptor": self.partner_id.street if self.partner_id.street else "-",
            # VERIFICAR
            "tipoDocReceptorAsociado": replace_false(self.partner_id.tipo_documento),
            "numDocReceptorAsociado": replace_false(self.partner_id.vat),
            "nombreReceptorAsociado": replace_false(
                self.partner_id.registration_name if self.partner_id.registration_name else self.partner_id.name),

            # "direccionDestino" : "",#solo para boletas
            "tipoMoneda": self.currency_id.name,
            "sustento": replace_false(self.sustento_nota),  # solo notas
            # solo_notas
            "tipoMotivoNotaModificatoria": str(self.tipo_nota_credito.code if self.invoice_type_code == "07" else self.tipo_nota_dedito.code),
            "mntNeto": round(self.total_venta_gravado, 2),
            "mntExe": round(self.total_venta_inafecto, 2),
            "mntExo": round(self.total_venta_exonerada, 2),
            "mntTotalIgv": round(self.amount_tax, 2),
            "mntTotal": round(self.amount_total, 2),
            # "mntTotalGrat": round(self.total_venta_gratuito, 2),  # solo para facturas y boletas
            "fechaVencimiento": self.date_due if self.date_due else now.strftime("%Y-%m-%d"),
            "glosaDocumento": "VENTA",  # verificar
            "codContrato": replace_false(self.number),
            # "codCentroCosto" : "",
            # verificar
            "tipoCambioDestino": round(self.tipo_cambio_fecha_factura, 4),
            "mntTotalIsc": 0.0,
            "mntTotalOtros": 0.0,
            "mntTotalOtrosCargos": 0.0,
            # "mntTotalAnticipos" : 0.0, #solo factura y boleta
            "tipoFormatoRepresentacionImpresa": "GENERAL",
            "mntTotalLetras": to_word(round(self.amount_total, 2), self.currency_id.name)
        },
        "descuento": {
            # "mntDescuentoGlobal": self.total_descuento_global,
            "mntTotalDescuentos": round(self.total_descuentos,2)
        },
        # solo factura y boleta
        # "servicioHospedaje": { },
        # solo factura y boleta, con expecciones

        "indicadores": {
            # VERIFICAR ESTOS CAMPOS

            # "indExportacion" : False,
            # "indNoDomiciliados" : False, #valido para notas
            # "indAnticipo" : True,
            # "indDeduccionAnticipos" : False,
            # "indServiciosHospedaje" : False,
            # "indVentaItinerante" : False,
            # "indTrasladoBienesConRepresentacionImpresa" : False,
            # "indVentaArrozPilado" : False,
            # "indComprobantePercepcion" : False,
            # "indBienesTransferidosAmazonia" : False,
            # "indServiciosPrestadosAmazonia" : False,
            # "indContratosConstruccionEjecutadosAmazonia" : False

        },

        # solo factura y boleta
        # "percepcion": {
        # "mntBaseImponible" : 0.0,
        # "mntPercepcion" : 0.0,
        # "mntTotalMasPercepcion" : 0.0,
        # "tasaPercepcion" : 1.0
        # },
        # "datosAdicionales": {},
    }
    data_impuesto = []
    data_detalle = []
    data_referencia = []  # solo para notas
    data_anticipo = []  # solo facturas y boletas
    data_anexo = []  # si hay anexos

    for tax in self.tax_line_ids:
        data_impuesto.append({
            "codImpuesto": str(tax.tax_id.tax_group_id.code),
            "montoImpuesto": round(tax.base,2),
            "tasaImpuesto": round(tax.tax_id.amount/100,2)
        })

    if len(self.tax_line_ids) == 0:
        data_impuesto.append({
            "codImpuesto": "1000",
            "montoImpuesto": 0.0,
            "tasaImpuesto": 0.18
        })

    for item in self.invoice_line_ids:
        price_unit = item.price_unit * \
            (1-(item.discount/100)) - item.descuento_unitario
        if (item.invoice_line_tax_ids.price_include):

            if (item.invoice_line_tax_ids.amount == 0):
                montoImpuestoUni = 0
                base_imponible = price_unit
            else:
                base_imponible = price_unit / \
                    (1 + (item.invoice_line_tax_ids.amount / 100))
                montoImpuestoUni = price_unit - base_imponible

            precioItem = price_unit

        else:
            montoImpuestoUni = price_unit * \
                (item.invoice_line_tax_ids.amount / 100)

            precioItem = price_unit + montoImpuestoUni
            base_imponible = price_unit

        '''
        data_impuesto.append({
            "codImpuesto": str(item.invoice_line_tax_ids.tax_group_id.code),
            "montoImpuesto": round(montoImpuestoUni * item.quantity, 2),
            "tasaImpuesto": round(item.invoice_line_tax_ids.amount / 100, 2)
        })
        
        '''
        tasaIgv = item.invoice_line_tax_ids[0].amount/100 if len(item.invoice_line_tax_ids) else ""
        montoItem = round((base_imponible) * item.quantity, 2)
        nombreItem = item.name.strip().replace("\n","")
        data_detalle.append({
            "cantidadItem": round(item.quantity, 3),
            "unidadMedidaItem": item.uom_id.code,
            "codItem": str(item.product_id.id),
            "nombreItem": nombreItem[0:250],
            "precioItem": round(precioItem, 2),
            "precioItemSinIgv": round(base_imponible, 2),
            "montoItem": round(item.product_id.lst_price*item.quantity,2)  if montoItem == 0  else montoItem,
            #"descuentoMonto": item.discount * precioItem / 100,  # solo factura y boleta
            "codAfectacionIgv":  item.invoice_line_tax_ids[0].tipo_afectacion_igv.code if len(item.invoice_line_tax_ids)>0 else False,
            "tasaIgv": round(tasaIgv*100,2),
            "montoIgv": round(montoImpuestoUni * item.quantity, 2),
            "codSistemaCalculoIsc": "01",  # VERIFICAR
            "montoIsc": 0.0,  # VERIFICAR
            # "tasaIsc" : 0.0, #VERIFICAR
            "precioItemReferencia" : round(item.product_id.lst_price,2),
            "idOperacion": str(self.id),
            "no_onerosa": True if item.no_onerosa else False
        })

        
    if self.invoice_type_code in ["07","08"]:
        if self.formato_comprobante_ref not in ["fisico","electronico"]:
            raise ValidationError("El formato del comprobante de referencia debe ser Físico o Electrónico")

        if self.formato_comprobante_ref == "fisico":
            if not self.comprobante_fisico_ref and not self.tipo_comprobante_ref:
                raise ValidationError("Cuando el tipo de comprobante de referencia es físico entonces, debe completar el campo de comprobante físico de referencia y el tipo de documento (Factura o Boleta)")
            else:
                if not re.match("^\d{4}-\d{1,8}$", self.comprobante_fisico_ref):
                    raise ValidationError("El Comprobante no posee el formato Requerido")
                    
                serieRef = self.comprobante_fisico_ref.split("-")[0]
                correlativoRef = self.comprobante_fisico_ref.split("-")[1]
                tipoDocumentoRef = self.tipo_comprobante_ref
                
                data_referencia.append({
                    'tipoDocumentoRef': tipoDocumentoRef,
                    'serieRef': serieRef,
                    'correlativoRef': correlativoRef,
                    'fechaEmisionRef': self.fecha_emision_comprobante_fisico_ref,
                    'numero': self.comprobante_fisico_ref
                })

        elif self.formato_comprobante_ref == "electronico":
            document_reference = self.refund_invoice_id
            data_referencia.append({
                'tipoDocumentoRef': document_reference.invoice_type_code,
                'serieRef': document_reference.number[0:4],
                'correlativoRef': int(document_reference.number[5:len(document_reference.number)]),
                'fechaEmisionRef': document_reference.date_invoice,
                'numero': document_reference.number
            })
            if document_reference.number[0] != self.journal_id.code[0]:
                raise UserError("Las Notas de Facturas deben iniciar con 'F' y las Notas de Boletas deben iniciar con 'B'")
        else:
            raise ValidationError("El Formato del Comprobante se Obligatorio")
    else:
        raise ValidationError("El código del tipo de comprobante debe ser 07 para Notas de Crédito o 08 para Notas de Débito")

    data["impuesto"] = data_impuesto
    data["detalle"] = data_detalle
    data["anticipos"] = data_anticipo
    data["anexos"] = data_anexo
    data["referencia"] = data_referencia

    return data


def crear_json_baja(self, tipo_resumen="RA"):
    now = datetime.datetime.now()
    data = {
        "tipoResumen": tipo_resumen,
        "fechaGeneracion": self.date_invoice,
        "idTransaccion": str(self.id),
        "resumen": {
            "id": self.contador,
            "tipoDocEmisor": self.company_id.partner_id.tipo_documento,
            "numDocEmisor": self.company_id.partner_id.vat,
            "nombreEmisor": self.company_id.partner_id.registration_name,
            "fechaReferente": self.date_invoice,
            "tipoFormatoRepresentacionImpresa": "GENERAL"
        }
    }

    data_detalle = []
    for document in self.invoice_ids:
        data_detalle.append({
            "serie": document.number[0:4],
            "correlativo": int(document.number[5:len(document.number)]),
            "tipoDocumento": document.invoice_type_code,
            "motivo": self.motivo
        })

    data['detalle'] = data_detalle

    return data
    # return json.dumps(data, indent=4)


def replace_false(dato):
    if dato:
        return dato
    else:
        return ""
