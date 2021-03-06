odoo.define('sun_pos_rounding_amount.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
        },
        renderElement: function(){
            this._super();
            var self =  this;
            this.$('.rounding').click(function(){
                self.toggle_rounding_button();
            });
        },
        toggle_rounding_button: function(){
            var self = this;
            var order = this.pos.get_order();
            var $rounding_elem = $('#pos-rounding');
            if($rounding_elem.hasClass('fa-toggle-off')){
                $rounding_elem.removeClass('fa-toggle-off');
                $rounding_elem.addClass('fa-toggle-on');
                order.set_rounding_status(true);
            } else if($rounding_elem.hasClass('fa-toggle-on')){
                $rounding_elem.removeClass('fa-toggle-on');
                $rounding_elem.addClass('fa-toggle-off');
                order.set_rounding_status(false);
            }
            this.render_paymentlines();
        },
    });
});
