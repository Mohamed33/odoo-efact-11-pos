odoo.define('aspl_pos_stock.models', function (require) {
"use strict";

    var module = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;
    var _t = core._t;

	module.load_fields("product.product", ['qty_available','type']);

	var _super_orderline = module.Orderline.prototype;
	module.Orderline = module.Orderline.extend({
		initialize: function(attr,options){
			_super_orderline.initialize.call(this,attr,options);
			this.set({
			    location_id: false,
			    location_name: false,
           })
		},
		set_location_id: function(location_id){
			this.set({
			    'location_id': location_id,
            })
		},
		set_location_name: function(location_name){
			this.set({
                'location_name': location_name,
            })
		},
		get_location_id: function(){
            return this.get('location_id');
		},
		get_location_name: function(){
            return this.get('location_name');
		},
		export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var default_stock_location = this.pos.config.stock_location_id ? this.pos.config.stock_location_id[0] : false
            var new_val = {
                location_id: this.get_location_id() || default_stock_location,
            }
            $.extend(lines, new_val);
            return lines;
        },
        can_be_merged_with: function(orderline){
        	var res = _super_orderline.can_be_merged_with.call(this, orderline);
        	if(this.get_location_id() !== this.pos.shop.id){
        		return false
        	}
        	return res
        },
	});

	var _super_order = module.Order.prototype;
	module.Order = module.Order.extend({
		cart_product_qnty: function(product_id,flag){
	    	var self = this;
	    	var res = 0;
	    	var order = self.pos.get_order();
	    	var orderlines = order.get_orderlines();
	    	if (flag){
	    		_.each(orderlines, function(orderline){
					if(orderline.product.id == product_id){
						res += orderline.quantity
					}
	    		});
				return res;
	    	} else {
	    		_.each(orderlines, function(orderline){
					if(orderline.product.id == product_id && !orderline.selected){
						res += orderline.quantity
					}
	    		});
	    		return res;
	    	}
	    },
		add_product: function(product, options){
			var self = this;
			if(options && options.force_allow){
				return _super_order.add_product.call(this, product, options);
			}
			var product_quaty = self.cart_product_qnty(product.id,true);
			if(self.pos.config.restrict_order && product.type != "service"){
	        	if(self.pos.config.prod_qty_limit){
	        		var remain = product.qty_available-self.pos.config.prod_qty_limit
	        		if(product_quaty>=remain){
	        			if(self.pos.config.custom_msg){
	        				alert(self.pos.config.custom_msg);
		        		} else{
		        			alert("Product Out of Stock");
		        		}
	    				return
		        	}
	        	}
        		if(product_quaty>=product.qty_available && !self.pos.config.prod_qty_limit){
	        		if(self.pos.config.custom_msg){
	        			alert(self.pos.config.custom_msg);
	        		} else{
	        			alert("Product Out of Stock");
	        		}
	    			return
	        	}
	        }
			_super_order.add_product.call(this, product, options);
	    },
	});

	var _modelproto = module.PosModel.prototype;
    module.PosModel = module.PosModel.extend({
    	load_server_data: function(){
    	    var self = this;
            var product_index = _.findIndex(this.models, function (model) {
                return model.model === "product.product";
            });
            var product_model = this.models[product_index];
            self.product_fields = product_model.fields;
            self.product_domain = product_model.domain;
            if (product_index !== -1) {
                this.models.splice(product_index, 1);
            }
            return _modelproto.load_server_data.apply(this, arguments)
            .then(function () {
    	        var context = product_model.context(self, {});
    	        _.extend(context, {
    	            'location': self.config.stock_location_id[0],
    	        })
                var param = {
                    model: 'product.product',
                    method: 'search_read',
                    domain: self.product_domain,
                    fields: self.product_fields,
                    context: context,
                };
                self.chrome.loading_message(_t('Loading') + 'product.product', 1);
                rpc.query(param, {async:false}).then(function(products){
                    self.db.add_products(_.map(products, function (product) {
                        product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                        return new module.Product({}, product);
                    }))
                });
    	    });
    	},
    	_save_to_server: function (orders, options) {
	        if (!orders || !orders.length) {
	            var result = $.Deferred();
	            result.resolve([]);
	            return result;
	        }
        	options = options || {};
	        var self = this;
	        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;
	        var order_ids_to_sync = _.pluck(orders, 'id');
            var args = [_.map(orders, function (order) {
                order.to_invoice = options.to_invoice || false;
                return order;
            })];
	        return rpc.query({
                model: 'pos.order',
                method: 'create_from_ui',
                args: args,
            }, {
                timeout: timeout,
                shadow: !options.to_invoice
            })
            .then(function (server_ids) {
	        	_.each(orders, function(order) {
	        		var lines = order.data.lines;
	        		_.each(lines, function(line){
	        		    if(line[2].location_id === self.config.stock_location_id[0]){
                            var product_id = line[2].product_id;
                            var product_qty = line[2].qty;
                            var product = self.db.get_product_by_id(product_id);
                            var remain_qty = product.qty_available - product_qty;
                            product.qty_available = remain_qty;
                            self.gui.screen_instances.products.product_list_widget.product_cache.clear_node(product.id)
                            var prod_obj = self.gui.screen_instances.products.product_list_widget;
                            var current_pricelist = prod_obj._get_active_pricelist();
                            if(current_pricelist){
                                prod_obj.product_cache.clear_node(product.id+','+current_pricelist.id);
                                prod_obj.render_product(product);
                            }
                            prod_obj.renderElement();
	        			}
	        		});
	        	});
	            _.each(order_ids_to_sync, function (order_id) {
	                self.db.remove_order(order_id);
				});
				
	            self.set('failed',false);
	            return server_ids;
	        })
	        .fail(function (error, event){
	            if(error.code === 200 ){    // Business Logic Error, not a connection problem
	                if (error.data.exception_type == 'warning') {
	                    delete error.data.debug;
	                }
	                if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
	                    self.gui.show_popup('error-traceback',{
	                        'title': error.data.message,
	                        'body':  error.data.debug
	                    });
	                }
	                self.set('failed',error)
	            }
	            console.error('Failed to send orders:', orders);
	        });
    	},
   	})

});