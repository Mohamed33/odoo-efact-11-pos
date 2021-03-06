odoo.define('pos_ticket_extend.pos_ticket_extend', function (require) {
"use strict";

var models = require('point_of_sale.models');

var PosModelSuper = models.PosModel;

//PosModelSuper.prototype.models[2].fields.push("logo");

models.load_fields("res.company", "logo");

});
