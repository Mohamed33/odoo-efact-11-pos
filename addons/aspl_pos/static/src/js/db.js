odoo.define('aspl_pos.db', function (require) {

	var DB = require('point_of_sale.DB');
	DB.include({
		init: function(options){
	       	this._super.apply(this, arguments);
	       	this.all_categories = {};
	       	this.product_by_name = {};
	       	this.prod_name_list = [];
	       	this.prod_by_ref = {};
	       	this.product_by_tmpl_id = [],
	       	this.order_write_date = null;
        	this.order_by_id = {};
        	this.order_sorted = [];
        	this.order_search_string = "";
	    },
	    add_categories: function(categories){
	        var self = this;
	        this.all_categories = categories;
	        this._super.apply(this, arguments);
	    },
	    get_all_categories : function() {
			return this.all_categories;
		},
		add_products: function(products){
			var self = this;
			this._super.apply(this, arguments);
			 for(var i = 0, len = products.length; i < len; i++){
				 var product = products[i];
				 if(product.name){
					 this.product_by_name[product.name] = product
					 this.prod_name_list.push(product.name);
					 this.prod_by_ref[product.default_code] = product;
					 this.product_by_tmpl_id[product.product_tmpl_id] = product;
				 }
			 }
		},
		get_product_by_name: function(name){
	        if(this.product_by_name[name]){
	            return this.product_by_name[name];
	        }
	        return undefined;
	    },
	    get_products_name: function(name){
	    	return this.prod_name_list;
	    },
	    get_product_by_reference: function(ref){
	    	return this.prod_by_ref[ref];
	    },
	    get_product_by_tmpl_id: function(id){
	    	return this.product_by_tmpl_id[id];
	    },
	    add_orders: function(orders){
            var updated_count = 0;
            var new_write_date = '';
            for(var i = 0, len = orders.length; i < len; i++){
                var order = orders[i];
                if ( new_write_date < order.write_date ) {
                    new_write_date  = order.write_date;
                }
                if (!this.order_by_id[order.id]) {
                    this.order_sorted.push(order.id);
                }
                this.order_by_id[order.id] = order;
                updated_count += 1;
            }
            this.order_write_date = new_write_date || this.order_write_date;
            if (updated_count) {
                // If there were updates, we need to completely
                this.order_search_string = "";
                for (var id in this.order_by_id) {
                    var order = this.order_by_id[id];
                    this.order_search_string += this._order_search_string(order);
                }
            }
            return updated_count;
        },
        _order_search_string: function(order){
            var str =  order.name;
            if(order.pos_reference){
                str += '|' + order.pos_reference;
            }
            if(order.partner_id){
                str += '|' + order.partner_id[1];
            }
            str = '' + order.id + ':' + str.replace(':','') + '\n';
            return str;
        },
        get_order_write_date: function(){
            return this.order_write_date;
        },
        get_order_by_id: function(id){
            return this.order_by_id[id];
        },
        search_order: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            var r;
            for(var i = 0; i < this.limit; i++){
                r = re.exec(this.order_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_order_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
	});
});