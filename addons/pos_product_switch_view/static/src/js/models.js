odoo.define("pos_product_switch_view.models", function (require) {
    "use strict";
    
    var pos_model = require('point_of_sale.models');
    
    pos_model.load_fields('pos.config',['pos_product_view']);
    
    
});
