from odoo import api,models,fields
import os
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
from datetime import datetime
import pytz
import json
from odoo.tools.profiler import profile
import logging
os.environ["TZ"] = "America/Lima"
_logger = logging.getLogger(__name__)

DIAS_VISITA = {
    "0":"DOMINGO",
    "1":"LUNES",
    "2":"MARTES",
    "3":"MIERCOLES",
    "4":"JUEVES",
    "5":"VIERNES",
    "6":"SABADO"
}

# class ResPartner(models.Model):
#     _inherit = "res.partner"

#     @api.model
#     def default_get(self, fields):
#         res = super(ResPartner, self).default_get(fields)
#         payment_term_id = self.env.ref("account.account_payment_term_immediate")
#         province_id = self.env.ref("odoope_toponyms.ubigeos_1401").id
#         state_id = self.env.ref("odoope_toponyms.ubigeos_14").id
#         country_id = self.env.ref("base.pe").id
#         res.update({
#             "property_payment_term_id":payment_term_id.id,
#             "country_id":country_id,
#             "province_id":province_id,
#             "state_id":state_id,
#             "user_id":self.env.uid
#         })
#         return res
        
    
#     @api.constrains('property_payment_term_id')
#     def _check_(self):
#         for record in self:
#             if not record.property_payment_term_id and record.type not in ["delivery","other"]:
#                 raise UserError("El campo plazos de pago es obligatorio")
            
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    qty_available = fields.Float("Cnt. disp. actual")
    line_available = fields.Boolean("Disponible")
    company_sucursal_id = fields.Many2one('res.company', 'sucursal', default=lambda self:self.env.user.company_id.id)
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

    @api.onchange('product_id','product_uom_qty','product_uom')
    def _onchange_product_qty_available(self):
        for record in self:
            if record.product_id and record.product_uom_qty and record.product_uom:
                if not record.product_id.is_combo:
                    record.qty_available = record.product_id.virtual_available*record.product_id.uom_id.factor_inv/record.product_uom.factor_inv
                    record.line_available = record.qty_available >= record.product_uom_qty
                else:
                    _min = 1000000000
                    for pr in record.product_id.combo_product_id:
                        cantidad_disponible = pr.product_quantity*pr.uom_id.factor_inv/pr.product_id.uom_id.factor_inv
                        cantidad_combos_por_producto = pr.product_id.virtual_available/cantidad_disponible
                        _min = min(_min,cantidad_combos_por_producto)

                    record.qty_available = _min
                    record.line_available = record.qty_available >= record.product_uom_qty
    
    def write(self, values):
        # for record in self:
        line_available = values.get("line_available") 
        if line_available == None:
            line_available = self.line_available
        if not line_available:
            raise UserError("No cuenta con unidades disponibles para algunos productos. Elimine los productos en rojo para poder guardar la venta. [{}]".format(self.name))
        
        return super(SaleOrderLine, self).write(values)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[('01','Factura'),('03','Boleta'),("00","Nota de Pedido")], 
        default="00",
        required=True)

    fecha_hora = fields.Char("Fecha y Hora")
    fecha_hora_confirmacion = fields.Char("Fecha de Confirmación",compute="_compute_fecha_confirmacion")
    user_id = fields.Many2one('res.users', string='Vendedor', index=True, default=lambda self: self.env.user.id)
    
    company_id = fields.Many2one('res.company', 'Compañía', default=lambda self:self.env.user.company_id.parent_id.id if self.env.user.company_id.parent_id else self.env.user.company_id.id)
    company_sucursal_id = fields.Many2one('res.company', 'Sucursal', default=lambda self:self.env.user.company_id.id)
    ruta_ids = fields.Many2many("cn.ruta",default=lambda self:self.env["cn.programacion.ruta"].search([('dia_visita','=',DIAS_VISITA.get(datetime.now().strftime("%w"))),('user_id','=',self.env.uid)]).mapped("ruta_id"))
    branch_id = fields.Many2one("res.branch",string="Sucursal",default = lambda self: self.env.user.branch_id.id)

    @api.multi
    def action_confirm(self):
        for line in self.order_line:
            line._onchange_product_qty_available()
            # _logger.warn(line.product_id.name,line.qty_available)
        return super(SaleOrder,self).action_confirm()

    @api.model
    def create(self, values):
        values.update({
            "company_id":self.env.user.company_id.parent_id.id if self.env.user.company_id.parent_id else self.env.user.company_id.id,
            "user_id":self.env.user.id
        })
        # _logger.info(values)
        # for line in self.order_line:
        #     if not line.line_available:
        #         raise UserError("No cuenta con unidades disponibles para algunos productos. Elimine los productos en rojo para poder guardar la venta.")
        result = super(SaleOrder, self).create(values)
        return result
    
    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        vals = super(SaleOrder,self)._prepare_invoice()
        vals.update({
            "branch_id":self.branch_id.id,
            "ruta_ids":self.ruta_ids.ids
        })
        return vals
        
    # @api.multi
    # def write(self, values):
    #     for line in self.order_line:
    #         if not line.line_available:
    #             raise UserError("No cuenta con unidades disponibles para algunos productos. Elimine los productos en rojo para poder guardar la venta.")
        
    #     result = super(SaleOrder, self).write(values)
    
    #     return result
    

    @api.depends('confirmation_date')
    def _compute_fecha_confirmacion(self):
        for record in self:
            record.fecha_hora_confirmacion = record.confirmation_date
    

    @api.onchange('partner_id')
    def _onchange_tipo_documento_cliente(self):
        for record in self:
            if record.partner_id.tipo_documento == '6':
                record.tipo_documento = '01'
            else:
                record.tipo_documento = '03'


    @api.model
    def default_get(self, flds):
        res = super(SaleOrder, self).default_get(flds)
        lima = pytz.timezone('America/Lima')
        date_order = datetime.now(lima).strftime("%Y-%m-%d %H:%M:%S")
        
        #date_order_utc = datetime.strptime(fields.Datetime.now(),"%Y-%m-%d %X").replace(tzinfo=timezone("UTC"))
        #date_order = date_order_utc.astimezone(timezone("America/Lima")).strftime("%Y-%m-%d %X")
        os.system("echo '%s'"%(date_order))
        res.update({
            "date_order":date_order,
            "fecha_hora":date_order
            # "company_id":self.env.user.company_id.parent_id.id if self.env.user.company_id.parent_id else self.env.user.company_id.id
        })
        os.system("echo '%s'"%(json.dumps(res)))
        return res

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        """ Notify newly subscribed followers of the last posted message.
            :param partner_ids : the list of partner to add as needaction partner of the last message
                                 (This excludes the current partner)
        """
        return