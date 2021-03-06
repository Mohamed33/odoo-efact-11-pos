odoo.define('aspl_pos_stock.screen', function (require) {
"use strict";
	var screens = require('point_of_sale.screens');
	var rpc = require('web.rpc');

	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var PopupWidget = require('point_of_sale.popups');
	
	screens.ProductListWidget.include({

        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.model = options.model;
            this.productwidgets = [];
            this.weight = options.weight || 0;
            this.show_scale = options.show_scale || false;
            this.next_screen = options.next_screen || false;

            this.click_product_handler = function(e){
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                if(product){
                    if($(e.target).attr('class') === "product-qty-low" || $(e.target).attr('class') === "product-qty"){
                        var prod = product;
                        var prod_info = [];
                        var total_qty = 0;
                        rpc.query({
                            model: 'stock.warehouse',
                            method: 'disp_prod_stock',
                            args: [
                                 prod.id,self.pos.shop.id
                            ]
                        }).then(function(result){
                        if(result){
                            prod_info = result[0];
                            total_qty = result[1];
                            $("[data-product-id='"+product.id+"']").find('.total_qty').html(product.qty_available)
                            self.gui.show_popup('product_qty_popup',{prod_info_data:prod_info,total_qty: total_qty,product: product});
                        }
                        }).fail(function (error, event){
                            if(error.code === -32098) {
                                alert("Server Down...");
                                event.preventDefault();
                           }
                        });
                    }else{
                        options.click_product_action(product);
                    }
                }
            };

            this.product_list = options.product_list || [];
            this.product_cache = new screens.DomCache();
        },
    });
	
    screens.OrderWidget.include({
    	set_value: function(val) {
            var self = this;
            var order = self.pos.get_order();
            var orderline = order.get_selected_orderline();
             if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity' && orderline.product.type != "service"){
                	var order_line_qnty = order.cart_product_qnty(orderline.product.id);
                	if(val != 'remove' || val != ''){
	                	var total_quantity = parseInt(order_line_qnty) + parseInt(val);
	                	var product = self.pos.db.get_product_by_id(orderline.product.id);
	                	if(self.pos.config.restrict_order){
				        	if(self.pos.config.prod_qty_limit){
				        		var product_qty_available = product.qty_available - total_quantity
				        		var remain = product.qty_available-self.pos.config.prod_qty_limit
				        		if(total_quantity>remain){
				        			if(self.pos.config.custom_msg){
				        				alert(self.pos.config.custom_msg);
				        				this.numpad_state.reset();
					        		} else{
					        			alert("Product Out of Stock");
					        			this.numpad_state.reset();
					        		}
			        				return
					        	}
				        	}
				        	if(total_quantity>product.qty_available && !self.pos.config.prod_qty_limit){
				        		if(self.pos.config.custom_msg){
				        			alert(self.pos.config.custom_msg);
				        			this.numpad_state.reset();
				        		} else{
				        			alert("Product Out of Stock");
				        			this.numpad_state.reset();
				        		}
			        			return
				        	} 
		        		} 
		        		order.get_selected_orderline().set_quantity(val);   
                	}
                } else {
                	this._super(val);
                }
            }
        },
    });
	
});
