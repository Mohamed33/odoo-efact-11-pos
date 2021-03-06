odoo.define('aspl_pos_stock.popup', function (require) {
"use strict";
	var PopupWidget = require('point_of_sale.popups');
	var gui = require('point_of_sale.gui');
	var ProductQtyPopupWidget = PopupWidget.extend({
	    template: 'ProductQtyPopupWidget',
	    show: function(options){
	        options = options || {};
	        this.prod_info_data = options.prod_info_data || false;
	        this.total_qty = options.total_qty || '';
	        this.product = options.product || false;
	        this._super(options);
	        this.renderElement();
	    },
	    click_confirm: function(){
	    	var self = this;
            var order = self.pos.get_order();
	        for(var i in this.prod_info_data){
	        	var loc_id = this.prod_info_data[i][2]
	        	if($("#"+loc_id).val() && Number($("#"+loc_id).val()) > 0){
					order.add_product(this.product,{quantity:$("#"+loc_id).val(),force_allow:true})
					order.get_selected_orderline().set_location_id(this.prod_info_data[i][2]);
					order.get_selected_orderline().set_location_name(this.prod_info_data[i][0]);
	        	}
	        }
	        this.gui.close_popup();
	    },
	});
	gui.define_popup({name:'product_qty_popup', widget: ProductQtyPopupWidget});

});