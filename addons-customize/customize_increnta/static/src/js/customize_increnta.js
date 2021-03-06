odoo.define('customize_increnta.customize_increnta',["point_of_sale.models"], function(require) {
    'use strict';
    var models = require('point_of_sale.models');
    var PosModelSuper = models.PosModel;
    PosModelSuper.prototype.models[17].fields.push("es_producto_maestro")
    PosModelSuper.prototype.models[17].domain.push(["es_producto_maestro","=",true])

})