// bi_pos_stock js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('bi_pos_stock.pos', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    //var Model = require('web.DataModel');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var time = require('web.time');
    var utils = require('web.utils');


    var _t = core._t;



	models.load_models({
        model: 'stock.location',
        fields: [],
        //ids:    function(self){ return [self.config.stock_location_id[0]]; },

        loaded: function(self, locations){
            var i;
            self.locations = locations[0];
            
    	    if (self.config.show_stock_location == 'specific')
    	    {

		        // associate the Locations with their quants.
		        var ilen = locations.length;
		        for(i = 0; i < ilen; i++){
		            if(locations[i].id === self.config.stock_location_id[0]){
					    var ayaz = locations[i];
					    self.locations = ayaz;
		            }
		        }
            }

        },
	});
	


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        
        initialize: function (session, attributes) {
            var product_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            product_model.fields.push('qty_available','incoming_qty','outgoing_qty','type');

            return _super_posmodel.initialize.call(this, session, attributes);
        },
        
        //########################################################################################
        load_product_qty:function(product){
            
            var product_qty_final = $("[data-product-id='"+product.id+"'] #stockqty");
            product_qty_final.html(product.qty_available)
            
        },
        //#########################################################################################
        
        
        push_order: function(order, opts){
            var self = this;
            var pushed = _super_posmodel.push_order.call(this, order, opts);
            var client = order && order.get_client();
            
            if (order){
                
                //##############################
                if (this.config.pos_display_stock === true && this.config.pos_stock_type == 'onhand' || this.config.pos_stock_type == 'available'){
                order.orderlines.each(function(line){
                    var product = line.get_product();
                    product.qty_available -= line.get_quantity();
                    self.load_product_qty(product);
                })
                }
                //##############################
                
                
                /*if (this.config.pos_display_stock === true && this.config.pos_stock_type == 'onhand' || this.config.pos_stock_type == 'available')
                {
		            order.orderlines.each(function(line){
		               var qty = line.quantity;
		               var qty_available = line.product.qty_available;
		               var ayaz = line.product.qty_available - line.quantity;
		               qty_available = ayaz;
		               
		               var product = self.db.get_product_by_id(line.product.id);
		               var all = $('.product');
						$.each(all, function(index, value) {
							var product_id = $(value).data('product-id');
							if (product_id == product.id)
							{
								$(value).find('#stockqty').html(qty_available);
							}
						});
		        
		            });
		        }*/
            }
            return pushed;
        }
    });
    
    screens.ProductScreenWidget.include({
        show: function() {
            var self = this;
            this._super();
            
    	    if (self.pos.config.show_stock_location == 'specific')
    	    {
			    var partner_id = this.pos.get_client();
		    	var location = self.pos.locations;


                rpc.query({
				        model: 'stock.quant',
				        method: 'get_stock_location_qty',
				        args: [partner_id ? partner_id.id : 0, location],
		            
		            }).then(function(output) {
		            		        
				       var all = $('.product');
						$.each(all, function(index, value) {
							var product_id = $(value).data('product-id');
						
							for (var i = 0; i < output.length; i++) {
								var product = output[i][product_id];
								$(value).find('#stockqty').html(product);
							}
						});
		        });
            
            }
            
        },
    });    
    
    screens.ProductListWidget.include({
		init: function(parent, options) {
		    var self = this;
		    this._super(parent,options);
		    this.model = options.model;
		    this.productwidgets = [];
		    this.weight = options.weight || 0;
		    this.show_scale = options.show_scale || false;
		    this.next_screen = options.next_screen || false;

		    this.click_product_handler = function(){
		        var product = self.pos.db.get_product_by_id(this.dataset.productId);
		        //console.log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~product",product);
		        
		        if (product.type == 'product' && self.pos.config.pos_allow_order == false)
		        {
				    // Deny POS Order When Product is Out of Stock
				    if (product.qty_available <= self.pos.config.pos_deny_order && self.pos.config.pos_allow_order == false)
				    {
				    	self.gui.show_popup('error',{
							'title': _t('Deny Order'),
				            'body': _t("Deny Order." + "(" + product.display_name + ")" + " is Out of Stock.")
				        });
				    }
				     
				    
				    
				    // Allow POS Order When Product is Out of Stock
				    else if (product.qty_available <= 0 && self.pos.config.pos_allow_order == false)
				    {
						self.gui.show_popup('error',{
							'title': _t('Error: Out of Stock'),
							'body': _t("(" + product.display_name + ")" + " is Out of Stock."),
						});
				    } else {
				    	options.click_product_action(product);
				    }
		        } else {
				    	options.click_product_action(product);
				    }
		        
		        
		        
		    };

		},
   
	});
    // End GiftPopupWidget start

    // Popup start

    var ValidQtyPopupWidget = popups.extend({
        template: 'ValidQtyPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
            var self = this;
            this._super(options);
        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            this.$('#back_to_products').click(function() {
            	self.gui.show_screen('products');
			});            	
        },

    });
    gui.define_popup({
        name: 'valid_qty_popup_widget',
        widget: ValidQtyPopupWidget
    });

    // End Popup start
    
    // ActionpadWidget start
    screens.ActionpadWidget.include({
		renderElement: function() {
		    var self = this;
		    this._super();
		    this.$('.pay').click(function(){
		        var order = self.pos.get_order();

		        var has_valid_product_lot = _.every(order.orderlines.models, function(line){
		            return line.has_valid_product_lot();
		        });
		        if(!has_valid_product_lot){
		            self.gui.show_popup('error',{
		                'title': _t('Empty Serial/Lot Number'),
		                'body':  _t('One or more product(s) required serial/lot number.'),
		                confirm: function(){
		                    self.gui.show_screen('payment');
		                },
		            });
		        }else{
		            self.gui.show_screen('payment');
		        }



    	    if (self.pos.config.show_stock_location == 'specific')
    	    {
			    var partner_id = self.pos.get_client();
		    	var location = self.pos.locations;


                rpc.query({
				        model: 'stock.quant',
				        method: 'get_stock_location_qty',
				        args: [partner_id ? partner_id.id : 0, location],
		            
		            }).then(function(output) {


						var lines = order.get_orderlines();
						var flag = 0;

						for (var i = 0; i < lines.length; i++) {
		                    for (var j = 0; j < output.length; j++) {
		                        var values = $.map(output[0], function(value, key) { 
								    var keys = $.map(output[0], function(value, key) {
									    if (lines[i].product.type == 'product' && self.pos.config.pos_allow_order == false && lines[i].product['id'] == key && lines[i].quantity > value){
										    //if (lines[i].product['id'] == key){
											    //if (lines[i].quantity > value) {
										    flag = flag + 1;
												    //self.gui.show_screen('payment');
											   //}else { //(line1.quantity > line1.product['qty_available']){
												    //flag = 0;
												    //self.gui.show_popup('valid_qty_popup_widget', {});
												    
												
											    //}
										    //}
									    }
								
								
								    });
									                        	
		                        });
		                    }
						}
						if(flag > 0){
						    self.gui.show_popup('valid_qty_popup_widget', {});
						}
						else{
						    self.gui.show_screen('payment');
						}
						
						
						
						/*var lines = order.get_orderlines();

						for (var i = 0; i < lines.length; i++) {
						
		                    for (var j = 0; j < output.length; j++) {
		                    
		                    var values = $.map(output[0], function(value, key) { 

								var keys = $.map(output[0], function(value, key) {

									if (lines[i].product.type == 'product'){
										if (lines[i].product['id'] == key){
											if (lines[i].quantity <= value) {
												self.gui.show_screen('payment');
											}else { //(line1.quantity > line1.product['qty_available']){
												self.gui.show_popup('valid_qty_popup_widget', {});
											}
										}
									}
								
								
								});
									                    	
		                    });
								
		                    }
						}*/
						                        
                                		               
		        });
            
            } else {
            
            
				// When Ordered Qty it More than Available Qty, Raise Error popup

				var lines = order.get_orderlines();

				for (var i = 0; i < lines.length; i++) {
				    
				    if (lines[i].product.type == 'product' && self.pos.config.pos_allow_order == false && lines[i].quantity > lines[i].product['qty_available']){
						//if (lines[i].quantity > lines[i].product['qty_available']) {
						    self.gui.show_popup('valid_qty_popup_widget', {});
						    break;
						//}
						
			    	}
			    	else { 
			             self.gui.show_screen('payment');   
				    }
				    
				    
				    /*if (lines[i].product.type == 'product'){
						if (lines[i].quantity <= lines[i].product['qty_available']) {
						    self.gui.show_screen('payment');
						}else { //(line1.quantity > line1.product['qty_available']){
			                self.gui.show_popup('valid_qty_popup_widget', {});
						}
			    	}*/
				}
				
			}	
						        
		    });
		    this.$('.set-customer').click(function(){
		        self.gui.show_screen('clientlist');
		    });
            
        },
    });  
    // End ActionpadWidget start
        

});
