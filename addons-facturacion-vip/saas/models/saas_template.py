# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import random
import string
import logging
from slugify import slugify

from odoo import models, fields, api, SUPERUSER_ID, sql_db, _, registry
from odoo.tools.safe_eval import test_python_expr
from odoo.exceptions import ValidationError, UserError
from odoo.addons.queue_job.job import job
from ..xmlrpc import rpc_auth, rpc_install_modules, rpc_code_eval

from odoo.service import db

import os
import shutil

_logger = logging.getLogger(__name__)

MANDATORY_MODULES = ['auth_quick']
DEFAULT_TEMPLATE_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""

DEFAULT_BUILD_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {{...}}
# You can specify places for variables that can be passed when creating a build like this:
# env['{key_name_1}'].create({{'subject': '{key_name_2}', }})
# When you need curly braces in build post init code use doubling for escaping\n\n\n\n"""

DEFAULT_NGINX = """server {
    listen 80;
    server_name database.dominio;
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Add Headers for odoo proxy mode
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Odoo-dbfilter "database";
    # log
    access_log /var/log/nginx/database.access.log;
    error_log /var/log/nginx/database.error.log;

    # Redirect longpoll requests to odoo longpolling port
    location /longpolling {
        proxy_pass http://odoo-chat;
    }

    # Redirect requests to odoo backend server
    location / {
        proxy_redirect off;
        proxy_pass http://odoo-server;
    }

    # common gzip
    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
    gzip on;

    # Page down
    error_page 502 /502.html;
    #location = /502.html {
    #    internal;
    #    root /opt/odoo-instances-manager/error-pages;
    #}
}"""

DEFAULT_DOMINIO = "superempresa.pe"

def random_password(length=32):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


class SAASTemplate(models.Model):
    _name = 'saas.template'
    _description = 'Database Template'

    name = fields.Char()
    password = fields.Char()
    dominio = fields.Char(default=DEFAULT_DOMINIO)
    url = fields.Char(compute = 'crear_url')
    template_demo = fields.Boolean('Install demo data', default=False)
    template_module_ids = fields.Many2many('saas.module', string="Modules to install")
    template_nginx = fields.Text('Archivo Ngnix',default=DEFAULT_NGINX)
    modulos = fields.Many2many('ir.module.module')

    template_post_init = fields.Text(
        'Template Initialization',
        default=DEFAULT_TEMPLATE_PYTHON_CODE,
        help='Python code to be executed once db is created and modules are installed')
    # TODO: need additional check on the possibility of using with format().
    #  Normal use of curly braces will cause an error
    build_post_init = fields.Text(
        'Build Initialization',
        default=DEFAULT_BUILD_PYTHON_CODE,
        help='Python code to be executed once build db is created from template')
    operator_ids = fields.One2many('saas.template.operator', 'template_id', string="Template's deployments")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('creating', 'Database Creating'),
        ('installing_modules', 'Modules installation'),
        ('post_init', 'Extra initialization'),
        ('done', 'Ready'),

    ], default='draft')

    @api.constrains('template_post_init')
    def _check_python_code(self):
        for r in self.sudo():
            msg = test_python_expr(expr=r.template_post_init.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.multi
    def action_create_build(self):
        self.ensure_one()
        if any([rec.state == 'done' for rec in self.operator_ids]):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Create Build',
                'res_model': 'saas.template.create_build',
                'src_model': 'saas.template',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('saas.saas_template_create_build').id,
                'target': 'new',
            }
        else:
            raise UserError(_('There are no ready template\'s deployments. Create new one or wait until it\'s done.'))

    def crear_url(self):
        for record in self:
            if record.name:
                record.url = record.name + '.' + record.dominio

    def crear_nginx(self):

        texto = self.template_nginx

        texto = texto.replace('database',self.name)
        self.template_nginx = texto.replace('dominio', self.dominio)

        f = open(self.name+".txt", "w")
        f.write(str(self.template_nginx))
        f.close()


        # Source path
        source = "file.txt"

        # Destination path
        destination = "file(copy).txt"

        # Copy the content of
        # source to destination
        dest = shutil.copyfile(source, destination)


    def crear_instancia(self):
        self.with_delay().crear_database()

    @job
    def crear_database(self):
        self.state = 'creating'
        db.exp_create_database( db_name=self.name, demo=False, lang='es_PE', user_password=self.password)

    def install_modulo(self):
        irModuleObj = self.env['ir.module.module']
        irModuleObj.update_list()
        moduleIds = irModuleObj.search(
            [
                ('state', '!=', 'installed'),
                ('name', '=', 'crm')
            ]
        )
        if moduleIds:
            moduleIds[0].button_immediate_install()

    def install_modulo2(self):
        self.ensure_one()
        #modules = [module.name for module in self.template_module_ids]
        #modules = [('name', 'in', MANDATORY_MODULES + modules)]
        modules = [module.name for module in self.modulos]
        modules = [('name', 'in', MANDATORY_MODULES + modules)]
        db = sql_db.db_connect(self.name)
        with api.Environment.manage(), db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            module_ids = env['ir.module.module'].search([('state', '=', 'uninstalled')] + modules)
            module_ids.button_immediate_install()

            # Some magic to force reloading registry in other workers
            #env.registry.registry_invalidated = True
            #env.registry.signal_changes()

    def instalar_modulos(self,modulos):
        #self.ensure_one()
        self.with_delay().install_modulo_lista(modulos)

    @job
    def install_modulo_lista(self,modulos):
        #self.ensure_one()
        #modules = [module.name for module in self.template_module_ids]
        self.state = 'installing_modules'
        modulos = [('name', 'in',  modulos)]
        db = sql_db.db_connect(self.name)
        with api.Environment.manage(), db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            module_ids = env['ir.module.module'].search([('state', '=', 'uninstalled')] + modulos)
            module_ids.button_immediate_install()

            # Some magic to force reloading registry in other workers
            #env.registry.registry_invalidated = True
            #env.registry.signal_changes()

    def terminar_instalacion(self):
        self.with_delay().terminar()


    @job
    def terminar(self):
        self.state = 'done'


    def get_status(self):
        resp = ""

        if (self.state=='creating'):
            resp +="Creando una nueva instancia para la empresa ....."
        if (self.state=='installing_modules'):
            resp += "Creando una nueva instancia para la empresa .....ok "
            resp += "\n"
            resp += "Instalando los modulos seleccionados .... "
        if (self.state == 'done'):
            resp +="Creando una nueva instancia para la empresa .....ok"
            resp += "\n"
            resp += "Instalando los modulos seleccionados .... ok"
            resp += "\n"
            resp += "La instalaccion ha terminado , puede ingresar en el siguiente link "
            resp += "\r\n"
            resp += self.url
        return resp

class SAASModules(models.Model):
    _name = 'saas.module'
    _description = 'Template\'s modules to install'
    name = fields.Char('Technical name', required=True)
    description = fields.Char()
    template_ids = fields.Many2many('saas.template')

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            if rec.description:
                result.append((rec.id, '%s (%s)' % (rec.description, rec.name)))
            else:
                result.append((rec.id, rec.name))
        return result


class SAASTemplateLine(models.Model):
    _name = 'saas.template.operator'
    _description = 'Template\'s Deployment'
    _rec_name = 'operator_db_name'

    template_id = fields.Many2one('saas.template', required=True, ondelete='cascade')
    operator_id = fields.Many2one('saas.operator', required=True)
    password = fields.Char('DB Password')
    operator_db_name = fields.Char(required=True, string="Template database name")
    operator_db_id = fields.Many2one('saas.db', readonly=True)
    operator_db_state = fields.Selection(related='operator_db_id.state', string='Database operator state')
    to_rebuild = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('creating', 'Database Creating'),
        ('installing_modules', 'Modules installation'),
        ('post_init', 'Extra initialization'),
        ('done', 'Ready'),

    ], default='draft')

    def preparing_template_next(self):
        template_operators = self.search([('to_rebuild', '=', True)])
        operators = template_operators.mapped('operator_id')

        # filter out operators which already have template creating
        def filter_free_operators(op):
            states = op.template_operator_ids.mapped('state')
            return all((s in ['draft', 'done'] for s in states))

        operators = operators.filtered(filter_free_operators)
        if not operators:
            # it's not a time to start
            return
        for t_op in template_operators:
            if t_op.operator_id not in operators:
                continue
            t_op._prepare_template()

            # only one template per operator
            operators -= t_op.operator_id

    def _prepare_template(self):
        for r in self:
            # delete db is there is one
            r.operator_db_id.drop_db()
            if not r.operator_db_id or r.operator_id != r.operator_db_id.operator_id:
                r.operator_db_id = self.env['saas.db'].create({
                    'name': r.operator_db_name,
                    'operator_id': r.operator_id.id,
                    'type': 'template',
                })
            password = random_password()
            self.env['saas.log'].log_db_creating(r.operator_db_id)

            r.write({
                'state': 'creating',
                'password': password,
            })
            r.operator_db_id.with_delay().create_db(
                None,
                r.template_id.template_demo,
                password,
                callback_obj=r,
                callback_method='_on_template_created')

    def _on_template_created(self):
        self.ensure_one()
        self.to_rebuild = False
        self.state = 'installing_modules'
        self.with_delay()._install_modules()

    @job
    def _install_modules(self):
        self.ensure_one()
        modules = [module.name for module in self.template_id.template_module_ids]
        modules = [('name', 'in', MANDATORY_MODULES + modules)]
        if self.operator_id.type == 'local':
            db = sql_db.db_connect(self.operator_db_name)
            with api.Environment.manage(), db.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                module_ids = env['ir.module.module'].search([('state', '=', 'uninstalled')] + modules)
                module_ids.button_immediate_install()
                # Some magic to force reloading registry in other workers
                env.registry.registry_invalidated = True
                env.registry.signal_changes()
        else:
            auth = self._rpc_auth()
            rpc_install_modules(auth, modules)
        self.state = 'post_init'
        self.with_delay()._post_init()

    @job
    def _post_init(self):
        if self.operator_id.type == 'local':
            db = sql_db.db_connect(self.operator_db_name)
            registry(self.operator_db_name).check_signaling()
            with api.Environment.manage(), db.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                action = env['ir.actions.server'].create({
                    'name': 'Local Code Eval',
                    'state': 'code',
                    'model_id': 1,
                    'code': self.template_id.template_post_init
                })
                action.run()
            self.state = 'done'
        else:
            auth = self._rpc_auth()
            rpc_code_eval(auth, self.template_id.template_post_init)
            self.state = 'done'

    def _rpc_auth(self):
        self.ensure_one()
        url = self.operator_db_id.get_url()
        return rpc_auth(
            url,
            self.operator_db_name,
            admin_username='admin',
            admin_password=self.password)

    def prepare_name(self, db_name):
        self.ensure_one()
        return slugify(db_name)

    @api.multi
    def create_db(self, key_values=None, db_name=None, with_delay=True):
        self.ensure_one()
        if not key_values:
            key_values = {}
        if not db_name:
            db_name = self.operator_id.generate_db_name()
        else:
            db_name = self.prepare_name(db_name)
        build = self.env['saas.db'].create({
            'name': db_name,
            'operator_id': self.operator_id.id,
            'type': 'build',
        })

        self.env['saas.log'].log_db_creating(build, self.operator_db_id)
        if with_delay:
            build.with_delay().create_db(
                self.operator_db_name,
                self.template_id.template_demo,
                self.password,
            )
            self.operator_id.with_delay().build_post_init(build, self.template_id.build_post_init, key_values)
        else:
            build.create_db(
                self.operator_db_name,
                self.template_id.template_demo,
                self.password,
            )
            self.operator_id.build_post_init(build, self.template_id.build_post_init, key_values)

        return build

    @api.multi
    def random_ready_operator(self):
        ready_operators = self.filtered(lambda r: r.state == 'done')
        return random.choice(ready_operators)
