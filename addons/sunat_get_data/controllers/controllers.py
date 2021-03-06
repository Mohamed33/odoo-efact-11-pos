# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from PIL import Image
import json
import argparse
import pytesseract
import os
from io import StringIO
import requests
from bs4 import BeautifulSoup


def esrucvalido(dato):
    largo_dato = len(dato)
    if dato is not None and dato != "" and dato.isdigit() and (largo_dato == 11 or largo_dato == 8):
        valor = int(dato)
        if largo_dato == 8:
            suma = 0
            for i in range(largo_dato-1):
                digito = int(dato[i]) - 0
                if i == 0:
                    suma = suma + digito * 2
                else:
                    suma = suma + digito * (largo_dato - 1)
                resto = suma % 11
                if resto == 1:
                    resto = 11
                if (resto + int(dato[largo_dato-1]) - 0) == 11:
                    return True

        elif largo_dato == 11:
            suma = 0
            x = 6
            for i in range(largo_dato - 1):
                if i == 4:
                    x = 8
                digito = int(dato[i]) - 0
                x = x - 1
                if x == 0:
                    suma = suma + digito * x
                else:
                    suma = suma + digito * x
            resto = suma % 11
            resto = 11 -resto
            if resto >= 10:
                resto = resto - 10
            if resto == int(dato[largo_dato - 1]) - 0:
                return True

        return False
    else:
        return False

def esdocvalido(dato, tipo):
    largo_dato = len(dato)
    if dato is not None and dato != "":
        if tipo == '1':
            if dato.isdigit() and largo_dato == 8:
                return True
        else:
            return True
    else:
        return False


class SunatGetData(http.Controller):
    @http.route(['/sunat_get_data/sunat/<int:tipoConsulta>/<string:search1>'], type='http', methods=['GET', 'POST'], auth="public", website=True, csrf=False)
    def index(self, tipoConsulta, search1, tipoDoc="", **post):
        flag_error = False
        data_error = []
        data_enviar = {}
        # VALIDACION
        if tipoConsulta == 1:
            if not esrucvalido(search1):
                flag_error = True
                data_error.append("Ruc no válido")
        elif tipoConsulta == 2:
            if len(search1) < 4 or tipoDoc not in ['1', '4', '7', 'A']:
                flag_error = True
                data_error.append("Documento no válido")
            elif not esdocvalido(search1, tipoDoc):
                flag_error = True
                data_error.append("Documento no válido")
        elif tipoConsulta == 3:
            if len(search1) < 4:
                flag_error = True
                data_error.append("Razón Social no válida")
        else:
            flag_error = True
            data_error.append("Método no válido")

        if flag_error:
            return request.make_response(json.dumps({
                'codeResponse': 400,
                'error': data_error
            }))

        s = requests.Session()
        r = s.get('http://www.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=image')
        f = open('/mnt/extra-addons/sunat_get_data/controllers/captcha.jpg', 'wb')
        with f:
            f.write(r.content)
            f.close()

        img = Image.open(StringIO.StringIO(r.content))
        captcha_val = pytesseract.image_to_string(img)

        # Tipo de Busqueda 1-RUC, 2-Tipo Documento, 3

        if tipoConsulta == 1:
            data_enviar["accion"] = 'consPorRuc'
            data_enviar["nroRuc"] = search1
            data_enviar["search1"] = search1
            data_enviar["tipdoc"] = ''
            data_enviar["search2"] = ''
            data_enviar["search3"] = ''
        elif tipoConsulta == 2:
            data_enviar["accion"] = 'consPorTipdoc'
            data_enviar["nroRuc"] = ''
            data_enviar["nrodoc"] = search1
            data_enviar["tipdoc"] = tipoDoc
            data_enviar["search1"] = ''
            data_enviar["search2"] = search1
            data_enviar["search3"] = ''
        else:
            data_enviar["accion"] = 'consPorRazonSoc'
            data_enviar["nroRuc"] = ''
            data_enviar["nrodoc"] = ''
            data_enviar["tipdoc"] = ''
            data_enviar["razSoc"] = search1
            data_enviar["search1"] = ''
            data_enviar["search2"] = ''
            data_enviar["search3"] = search1

        data_enviar["rbtnTipo"] = tipoConsulta
        data_enviar["contexto"] = "ti-it"
        data_enviar["modo"] = "1"
        data_enviar["codigo"] = captcha_val

        consult = s.post('http://www.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias', data=data_enviar)

        f = open('/mnt/extra-addons/sunat_get_data/controllers/response.html', 'w')
        with f:
            f.write(consult.text.encode('utf-8'))
            f.close()

        soup = BeautifulSoup(consult.text, 'html.parser')
        table = soup.find("table")
        if len(table) > 1:
            rows = table.find_all("tr")
            datos = {}
            rucNombre = rows[0].find_all("td")[1].get_text()
            datos["ruc"] = rucNombre[0:11]
            datos["nombre"] = rucNombre[14:]
            datos["tipoContribuyente"] = rows[1].find_all("td")[1].get_text()
            i = 0
            if datos["ruc"][0:2] == '10':
                i = 0
                datos["tipoDoc"] = "06"
                datos["tipoPersona"] = "PN"
                datos["tipoDocumento"] = rows[2 + i].find_all("td")[1].get_text().replace("\n", "").replace("\t","").replace( "\r", "").replace("   ", "")
                datos["profesion"] = rows[6 + i].find_all("td")[3].get_text().strip()
            elif datos["ruc"][0:2] == '20':
                i = -1
                datos["tipoDoc"] = "01"
                datos["tipoPersona"] = "PJ"
            datos["nombreComercial"] = rows[3 + i].find_all("td")[1].get_text()
            datos["fechaInscripcion"] = rows[4 + i].find_all("td")[1].get_text()
            datos["fechaIniActividades"] = rows[4 + i].find_all("td")[3].get_text().strip()
            datos["estado"] = rows[5 + i].find_all("td")[1].get_text().strip()
            datos["condicionContribuyente"] = rows[6 + i].find_all("td")[1].get_text().strip()
            datos["domicilioFiscal"] = rows[7 + i].find_all("td")[1].get_text().strip()
            dom_split = datos["domicilioFiscal"].split("-")
            if len(dom_split) == 3:
                datos["domicilioFiscal"] = dom_split[0]
                datos["provincia"] = dom_split[1]
                datos["distrito"] = dom_split[2]
            else:
                datos["provincia"] = ""
                datos["distrito"] = ""
            datos["sistemaEmision"] = rows[8 + i].find_all("td")[1].get_text().strip()
            datos["actividadComercioExterior"] = rows[8 + i].find_all("td")[3].get_text().strip()
            datos["sistemaContabilidad"] = rows[9 + i].find_all("td")[1].get_text().strip()
            act_econ = []
            for opt in rows[10 + i].find_all("td")[1].find_all("option"):
                act_econ.append(opt.get_text())
            datos["actEconomicas"] = act_econ
            comprobantes = []
            for opt in rows[11 + i].find_all("td")[1].find_all("option"):
                comprobantes.append(opt.get_text())
            datos["comprobantesElec"] = comprobantes
            sistemEmision = []
            for opt in rows[12 + i].find_all("td")[1].find_all("option"):
                sistemEmision.append(opt.get_text())
            datos["sistemasEmision"] = sistemEmision
            datos["fechaInicioEmisorE"] = rows[13 + i].find_all("td")[1].get_text().strip()
            datos["comElectronica"] = rows[14 + i].find_all("td")[1].get_text().strip()
            datos["fechaPLE"] = rows[15 + i].find_all("td")[1].get_text().strip()
            padrones = []
            for opt in rows[16 + i].find_all("td")[1].find_all("option"):
                padrones.append(opt.get_text())
            datos["padrones"] = padrones
            return request.make_response(json.dumps({
                'codeResponse': consult.status_code,
                'data': datos
            }))
        else:
            return request.make_response(json.dumps({
                'codeResponse': consult.status_code,
                'error': 'No se pudo conectar al servidor'
            }))

