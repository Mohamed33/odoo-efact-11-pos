from odoo import models,fields,api


class ResPartner(models.Model):
    _inherit = "res.partner"
    vehicle_ids = fields.Many2many("res.vehicle","propiedad","partner_id","vehicle_id")


class Vehicle(models.Model):
    _name = "res.vehicle"
    _rec_name = "placa"

    placa = fields.Char("Placa")
    marca = fields.Char("Marca")
    modelo = fields.Char("Modelo")
    anio_fabricacion = fields.Char("Año de Fabricación")
    km = fields.Float("Km")
    fecha_ultimo_servicio = fields.Date("Fecha de último servicio")
    km_ultimo_servicio = fields.Float("Km de último servicio")
    partner_ids = fields.Many2many("res.partner","propiedad","vehicle_id","partner_id")
    
    @api.model
    def create_from_ui(self, vehicle):
        vehicle_id = vehicle.pop('id', False)
        if vehicle_id:
            self.browse(vehicle_id).write(vehicle)
        else:
            vehicle['lang'] = self.env.user.lang
            vehicle_id = self.create(vehicle).id
        return vehicle_id