odoo.define('aspl_pos_internal_transfer.transfer_stock', function (require) {
"use strict";

var models = require('point_of_sale.models');
var DB = require('point_of_sale.DB');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;

	models.PosModel.prototype.models.push({
		model:  'stock.picking.type',
		fields: [],
		domain: [['code','=','internal']],
		loaded: function(self,stock_pick_typ){
			self.stock_pick_typ = stock_pick_typ;
			self.db.add_picking_types(stock_pick_typ);
		},
	},{
		model:  'stock.location',
		fields: [],
		domain: [['usage','=','internal']],
		loaded: function(self,stock_location){
			self.stock_location = stock_location;
		},
	});

	/* Internal TransferButton */
	var InternalTransferButton = screens.ActionButtonWidget.extend({
	    template : 'InternalTransferButton',
	    button_click : function() {
	        var self = this;
	        var selectedOrder = this.pos.get_order();
	        var currentOrderLines = selectedOrder.get_orderlines();
	        if(self.pos.stock_pick_typ.length == 0){
	        	return alert(_t("You can not proceed with 'Manage only 1 Warehouse with only 1 stock location' from inventory configuration."));
	        }
	        if(currentOrderLines.length == 0){
	        	return alert(_t("You can not proceed with empty cart."));
	        }
	        this.gui.show_popup('int_trans_popup',{'stock_pick_types':self.pos.stock_pick_typ,'location':self.pos.stock_location});
	    },
	});

	screens.define_action_button({
	    'name' : 'int_trans_btn',
	    'widget' : InternalTransferButton,
	    'condition': function(){
	            return this.pos.config.enable_int_trans_stock;
	    },
	});

	DB.include({
		init: function(options){
		    this._super.apply(this, arguments);
		    this.picking_type_by_id = {};
		},
		add_picking_types: function(stock_pick_typ){
			var self = this;
			stock_pick_typ.map(function(type){
				self.picking_type_by_id[type.id] = type;
			});
		},
		get_picking_type_by_id: function(id){
			return this.picking_type_by_id[id]
		}
	});

	var InternalTransferPopupWidget = PopupWidget.extend({
	    template: 'InternalTransferPopupWidget',
	    show: function(options){
	        options = options || {};
	        var self = this;
	        this.picking_types = options.stock_pick_types || [];
	        this.location = options.location || [];
	        this._super(options);
	        this.renderElement();
	        var pick_type = Number($('#pick_type').val());
	        var selected_pick_type = self.pos.db.get_picking_type_by_id(pick_type);
	        if(selected_pick_type && selected_pick_type.default_location_src_id[0]){
	        	$('#src_loc').val(selected_pick_type.default_location_src_id[0]);
	        }
	        if(selected_pick_type && selected_pick_type.default_location_dest_id[0]){
	        	$('#dest_loc').val(selected_pick_type.default_location_dest_id[0]);
	        }
	        $('#pick_type').change(function(){
	        	var pick_type = Number($(this).val());
	        	var selected_pick_type = self.pos.db.get_picking_type_by_id(pick_type);
	            if(selected_pick_type && selected_pick_type.default_location_src_id[0]){
	            	$('#src_loc').val(selected_pick_type.default_location_src_id[0]);
	            }
	            if(selected_pick_type && selected_pick_type.default_location_dest_id[0]){
	            	$('#dest_loc').val(selected_pick_type.default_location_dest_id[0]);
	            }
	        });
	    },
	    click_confirm: function(){
	    	var self = this;
	    	var selectedOrder = this.pos.get_order();
	        var currentOrderLines = selectedOrder.get_orderlines();
	        var moveLines = [];
	        _.each(currentOrderLines,function(item) {
	           var data = {}
	           var nm = item.product.default_code ? "["+ item.product.default_code +"]"+ item.product.display_name  : "";
	           data['product_id'] = item.product.id;
	           data['name'] = nm || item.product.display_name;
	           data['product_uom_qty'] = item.get_quantity();
	           data['location_id'] =  Number($('#src_loc').val());
	           data['location_dest_id'] = Number($('#dest_loc').val());
	           data['product_uom'] = item.product.uom_id[0];
	           
	           moveLines.push(data);
	        });
	        
	        var data = {}
	        data['moveLines'] = moveLines;
	        data['picking_type_id'] = Number($('#pick_type').val());
	        data['location_src_id'] =  Number($('#src_loc').val());
	        data['location_dest_id'] = Number($('#dest_loc').val());
	        data['state'] = $('#state').val();

	        var params = {
	        	model: 'stock.picking',
	        	method: 'do_detailed_internal_transfer',
	        	args: [{ data:data }],
	        }
	        rpc.query(params, {async: false})
	    	.then(function(result){
	    		if(result && result[0] && result[0]){
	    			var url = window.location.origin + '#id=' + result[0] + '&view_type=form&model=stock.picking';
	    			self.pos.gui.show_popup('stock_pick', {'url':url, 'name':result[1]});
	    		}
	    	});
	    },
	});
	gui.define_popup({name:'int_trans_popup', widget: InternalTransferPopupWidget});

	var StockPickPopupWidget = PopupWidget.extend({
	    template: 'StockPickPopupWidget',
	    click_confirm: function(){
	    	var self = this;
	    	self.clear_cart();
	        this.gui.close_popup();
	    },
	    clear_cart: function(){
        	var self = this;
        	var order = this.pos.get_order();
        	var currentOrderLines = order.get_orderlines();
        	if(currentOrderLines && currentOrderLines.length > 0){
        		_.each(currentOrderLines,function(item) {
        			order.remove_orderline(item);
                });
        	} else {
        		return
        	}
        	self.clear_cart();
        },
	});
	gui.define_popup({name:'stock_pick', widget: StockPickPopupWidget});

});
