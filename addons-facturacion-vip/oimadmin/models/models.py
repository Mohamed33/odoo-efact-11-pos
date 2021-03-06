# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import jwt
import time
import requests
import os,json

class OimAdminServer(models.Model):
    _name = 'oimadmin.servers'

    name = fields.Char(string="Nombre")
    url = fields.Char(string="Url", required=True)
    api_key = fields.Char(string="Api Key", required=True)
    api_secret = fields.Char(string="Api Secret", required=True)

    instances_ids = fields.One2many("oimadmin.odooinstances", "oim_server_id", string="Odoo Instancias")
    dbservers_ids = fields.One2many("oimadmin.dbservers", "oim_server_id", string="DB-Servers")

    def generate_token(self, time_valid=10):
        headers = {
            "iss": self.api_key
        }
        payload = {
            "exp": int(time.time()) + time_valid,
        }
        token = jwt.encode(payload, self.api_secret, 'HS256', headers)
        return token

    def get_token_header(self, **kwargs):
        return {
            "x-oim-auth": self.generate_token(**kwargs)
        }

    def get_instances(self, skip=0, size=50):
        try:
            ans = requests.get(self.url + "/instance",
                               headers=self.get_token_header(),
                               params={"skip": skip, "size": size}).json()
        except Exception as e:
            raise exceptions.UserError(str(e))
        if not ans['success']:
            raise exceptions.UserError(ans['message'])
        return ans['data']

    def get_dbservers(self, skip=0, size=50):
        try:
            ans = requests.get(
                self.url + "/db-server",
                headers=self.get_token_header(),
                params={"skip": skip, "size": size}).json()
        except Exception as e:
            raise exceptions.UserError(str(e))
        if not ans['success']:
            raise exceptions.UserError(ans['message'])
        return ans['data']

    def action_test_connection(self):
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        self.get_instances(size=1)
        raise exceptions.Warning("Sucessfull connection.")

    def action_syncronize(self):
        dbservers = self.get_dbservers()

        for dbserver in dbservers:
            dbserver['oim_server_id'] = self.id
            self.env['oimadmin.dbservers'].create(dbserver, False)

        instances = []
        while True:
            tmp = self.get_instances(skip=len(instances))
            if len(tmp) == 0:
                break
            instances.extend(tmp)

        for instance in instances:
            dbcode = instance['database_server']
            del instance['database_server']
            instance['oim_server_id'] = self.id
            instance['database_server_id'] = self.env['oimadmin.dbservers'].search([('code', '=', dbcode)], limit=1).id
            
            os.system("echo '{}'".format(json.dumps(instance,indent=4)))
            
            if instance["database_server_id"] and  instance["database_name"]:
                if not self.env["oimadmin.odooinstances"].search([["code","=",instance["code"]]]):
                    self.env['oimadmin.odooinstances'].create(instance, remote_create = False)


class OimAdminDbServer(models.Model):
    _name = 'oimadmin.dbservers'
    _rec_name = "host"

    code = fields.Char("Code")
    host = fields.Char("Host", required=True)
    port = fields.Integer("Port", default=5432, required=True)
    username = fields.Char("Username", required=True)
    password = fields.Char("Password", required=True)
    limit = fields.Integer("Limit", default=0)
    conn_test = fields.Boolean("Connection Tested?")

    oim_server_id = fields.Many2one("oimadmin.servers", "Oim Server", required=True)
    instances_ids = fields.One2many("oimadmin.odooinstances", "database_server_id", string="Odoo Instancias")

    def action_test_connection(self):
        if not self.code:
            raise exceptions.UserError("Primero guardar")

        oim_server = self.oim_server_id
        url = oim_server.url + "/db-server/" + self.code + "/test"
        resp = requests.post(url, headers=oim_server.get_token_header()).json()
        self.conn_test = resp['success'] # not working
        raise exceptions.Warning("Successfull Connection" if resp['success'] else "No connection")

    @api.model
    def create(self, vals, remote_create=True):
        oim_server = self.env['oimadmin.servers'].browse([vals['oim_server_id']])[0]
        url = oim_server.url + "/db-server"
        if remote_create:
            resp = requests.post(url, headers=oim_server.get_token_header(), json=vals).json()
            if not resp['success']:
                raise exceptions.UserError(resp['error'])

            vals.update(resp['server'])
        return super(OimAdminDbServer, self).create(vals)

    @api.multi
    def write(self, vals):
        oim_server = self.oim_server_id
        url = oim_server.url + "/db-server/" + self.code
        resp = requests.put(url, headers=oim_server.get_token_header(), json=vals).json()
        if not resp['success']:
            raise exceptions.UserError(resp['error'])
        if resp.get('message', None) != "ok":
            vals['conn_test'] = False
        return super(OimAdminDbServer, self).write(vals)
    
    @api.multi
    def unlink(self):
        oim_server = self.oim_server_id
        url = oim_server.url + "/db-server/" + self.code
        resp = requests.delete(url, headers=oim_server.get_token_header()).json()
        if not resp['success']:
            raise exceptions.UserError(resp['error'])
        return super(OimAdminDbServer, self).unlink()


class OimAdminOdooInstances(models.Model):
    _name = 'oimadmin.odooinstances'
    _rec_name = "domain"

    code = fields.Char("Codigo")
    domain = fields.Char("Dominio", required=True)
    ssl_enabled = fields.Boolean("Ssl Habilitao?", default=False)
    docker_server = fields.Char("Docker Server")
    port = fields.Integer("Port")
    port_chat = fields.Integer("Chat Port")
    docker_instance_name = fields.Char("Docker Instance Name")
    docker_image = fields.Char("Docker Image", default="odoo")
    docker_tag = fields.Char("Docker Image Tag", default="11")
    odoo_conf_template = fields.Char("Odoo template Config", default="odoo12")
    database_name = fields.Char("Database Name")

    oim_server_id = fields.Many2one("oimadmin.servers", "Oim Server", required=True)
    database_server_id = fields.Many2one("oimadmin.dbservers", "Database Server", required=True)

    # Helper fields
    reboot_command = fields.Char("Reboot Command", default="")
    cert_crt = fields.Text("SSL Certificate Public", default="")
    cert_key = fields.Text("SSL Certificate Key", default="")

    @api.model
    def create(self, vals, remote_create=True):
        oim_server = self.env['oimadmin.servers'].browse([vals['oim_server_id']])[0]
        url = oim_server.url + "/instance"

        data = {
            "domain": vals["domain"],
            "docker-image": vals['docker_image'],
            "docker-tag": vals['docker_tag'],
            "odoo-conf-template": vals["odoo_conf_template"],
            "db-server": self.env['oimadmin.dbservers'].browse(vals['database_server_id'])[0].code if self.env['oimadmin.dbservers'].browse(vals['database_server_id']) else False
        }   
        if remote_create:
            resp = requests.post(url, headers=oim_server.get_token_header(), json=data).json()
            if not resp['success']:
                raise exceptions.UserError(resp['error'])

            del resp['instance']['database_server']
            vals.update(resp['instance'])
        return super(OimAdminOdooInstances, self).create(vals)

    @api.multi
    def write(self, vals):
        read_only = ["domain", "docker_image", "docker_tag", "odoo_conf_template", "oim_server_id", "database_server_id"]
        if sum([1 if x in vals else 0 for x in read_only]) > 0:
            raise exceptions.Warning("Edit option disabled.")
        super(OimAdminOdooInstances, self).write(vals)

    @api.multi
    def unlink(self):
        oim_server = self.oim_server_id
        url = oim_server.url + "/instance/" + self.code
        resp = requests.delete(url, headers=oim_server.get_token_header()).json()
        if not resp['success']:
            raise exceptions.UserError(resp['error'])
        return super(OimAdminOdooInstances, self).unlink()

    def action_syncronize(self):
        oim_server = self.oim_server_id
        url = oim_server.url + "/instance/" + self.code

        resp = requests.get(url, headers=oim_server.get_token_header()).json()
        if not resp['success']:
            raise exceptions.Warning(resp.get('error', 'error'))

        vals = resp['data']
        vals['database_server_id'] = self.env['oimadmin.dbservers'].search([('code', '=', vals['database_server'])], limit=1).id
        del vals['database_server']
        super(OimAdminOdooInstances, self).write(vals)
    
    def run_command(self, command, reboot_commad=""):
        if command not in ['start', 'stop', 'restart', "reboot"]:
            raise exceptions.Warning("Bad command.")

        oim_server = self.oim_server_id
        url = oim_server.url + "/instance/" + self.code  + "/" + command

        data = {
            "command": reboot_commad
        }
        resp = requests.post(url, headers=oim_server.get_token_header(), json=data).json()
        if not resp['success']:
            raise exceptions.Warning(resp.get('error', 'error'))

    def action_start(self):
        self.run_command("start")

    def action_stop(self):
        self.run_command("stop")

    def action_restart(self):
        self.run_command("restart")

    def action_reboot(self):
        self.run_command("reboot", self.reboot_command)


    def action_upload_ssl(self):
        oim_server = self.oim_server_id
        url = oim_server.url + "/nginx/" + self.code + "/upload-cert"

        data = {
            "cert-crt": self.cert_crt,
            "cert-key": self.cert_key,
            "configure-nginx": False
        }

        resp = requests.post(url, headers=oim_server.get_token_header(), json=data).json()
        if not resp['success']:
            raise exceptions.Warning(resp.get("error", "error."))
    
    def configure_nginx(self, command):
        if command not in ['configure', "enable-ssl", "disable-ssl"]:
            raise exceptions.Warning("Bad command.")

        oim_server = self.oim_server_id
        url = oim_server.url + "/nginx/" + self.code  + "/" + command
  
        resp = requests.post(url, headers=oim_server.get_token_header()).json()
        if not resp['success']:
            raise exceptions.Warning(resp.get('error', 'error'))

        self.action_syncronize()

    def action_configure_nginx(self):
        self.configure_nginx("configure")

    def action_ssl_enable(self):
        self.configure_nginx("enable-ssl")
    
    def action_ssl_disable(self):
        self.configure_nginx("disable-ssl")
