# -*- coding: utf-8 -*-

from odoo import models, fields, api

class archivo (models.Model):
    _name = "letra_cambio.archivo"

    name =  fields.Char()
    fecha = fields.Date()
    doc1 = fields.One2many('letra_cambio.documento','pest1', string='pestaña1')
    doc2 = fields.One2many('letra_cambio.documento', 'pest2' , string='pestaña2' )
    #doc = fields.Many2one('letra_cambio.documento', string='archivo1')
    #doc2 = fields.Many2many('letra_cambio.documento','inter2','name','archivo2',string='pestaña2')


class documento (models.Model):
    _name = "letra_cambio.documento"

    name =  fields.Char()
    fecha = fields.Date()
    pest1 = fields.Many2one('letra_cambio.archivo',string='archivo1' )
    pest2 = fields.Many2one('letra_cambio.archivo',string='archivo2' )