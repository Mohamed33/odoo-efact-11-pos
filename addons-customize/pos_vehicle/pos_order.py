from odoo import fields,api,models
import json
import os
class PosOrder(models.Model):
    _inherit = "pos.order"
    vehicle_id = fields.Many2one("res.vehicle")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder,self)._order_fields(ui_order)
        vehicle = ui_order["vehicle"]
        if vehicle:
            res["vehicle_id"] = vehicle["id"]
        return res        

    @api.multi
    def print_pos_receipt(self):
        res = super(PosOrder,self).print_pos_receipt()
        if self.vehicle_id:
            res["vehicle"] = {
                "placa":self.vehicle_id.placa,
                "marca":self.vehicle_id.marca,
                "modelo":self.vehicle_id.modelo
            }
        return res