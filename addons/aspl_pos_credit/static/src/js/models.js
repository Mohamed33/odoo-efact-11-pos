odoo.define('aspl_pos_credit.models', function (require) {
	var models = require('point_of_sale.models');
	var rpc = require('web.rpc');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;

    models.load_fields("res.partner", ['remaining_credit_amount','property_account_receivable_id','parent_id']);
    models.load_fields("account.journal", ['pos_journal_id']);
    models.load_fields("pos.order", ['is_delivery'], ['picking_id']);

	var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options){
	        var self = this;
	        var res = _super_Order.initialize.call(this, attr, options);
	        this.set({
	            'paying_order': false,
	            type_for_credit: false,
                change_amount_for_credit: false,
                use_credit: false,
        		amount_due: this.get_due() ? this.get_due() : 0.00,
                is_delivery: false,
                credit_detail: [],
                customer_credit:false,
	        })
	        return res;
	    },
	    set_credit_mode: function(credit_mode) {
            this.credit_mode = credit_mode;
        },
        get_credit_mode: function() {
            return this.credit_mode;
        },
	    set_credit_detail: function(credit_detail) {
	        var data = this.get('credit_detail')
	        data.push(credit_detail);
	        this.set('credit_detail',data);
        },
        get_credit_detail: function() {
            return this.get('credit_detail')
        },
        set_customer_credit:function(){
            var data = this.get('customer_credit')
	        data = true;
	        this.set('customer_credit',data);
        },
        get_customer_credit: function() {
            return this.get('customer_credit')
        },
	    add_paymentline: function(cashregister) {
            this.assert_editable();
            var newPaymentline = new models.Paymentline({},{order: this, cashregister:cashregister, pos: this.pos});
            if(cashregister.journal.type == 'bank'){
                if(this.pos.get_order().get_total_with_tax() >= 0){
                    newPaymentline.set_amount( Math.max(this.pos.get_order().get_total_with_tax(),0) );
                }else {
                    newPaymentline.set_amount( Math.min(this.pos.get_order().get_total_with_tax(),0) );
                }
            }
            this.paymentlines.add(newPaymentline);
            this.select_paymentline(newPaymentline);
        },
        add_paymentline_by_journal: function(cashregister) {
            this.assert_editable();
            var newPaymentline = new models.Paymentline({}, {order: this, cashregister:cashregister, pos: this.pos})
            var newPaymentline = new models.Paymentline({}, {order: this, cashregister:cashregister, pos: this.pos})
            if((this.pos.get_order().get_due() > 0) && (this.pos.get_order().get_client().remaining_credit_amount > this.pos.get_order().get_due())) {
                newPaymentline.set_amount(Math.min(this.pos.get_order().get_due(),this.pos.get_order().get_client().remaining_credit_amount));
            }else if((this.pos.get_order().get_due() > 0) && (this.pos.get_order().get_client().remaining_credit_amount < this.pos.get_order().get_due())) {
                newPaymentline.set_amount(Math.min(this.pos.get_order().get_due(),this.pos.get_order().get_client().remaining_credit_amount));
            }else if(this.pos.get_order().get_due() > 0) {
                    newPaymentline.set_amount( Math.max(this.pos.get_order().get_due(),0) );
            }
            this.paymentlines.add(newPaymentline);
            this.select_paymentline(newPaymentline);
        },
        set_records: function(records) {
    	    this.records = records;
    	},
    	get_records: function() {
    	    return this.records;
    	},
    	get_remaining_credit(){
    		var credit_total = 0.00,use_credit = 0.00;
    		var self = this;
    		var partner = self.pos.get_client();
            if(partner){
                var client_account = partner.deposite_info['content'];
                var credit_detail = this.get_credit_detail();
                _.each(client_account, function(values){
                    credit_total = values.amount + credit_total
                });
                if(credit_detail && credit_detail.length > 0 && client_account && client_account.length > 0){
                	for (var i=0;i<client_account.length;i++){
            			for(var j=0;j<credit_detail.length;j++){
                    		if(client_account[i].id == credit_detail[j].journal_id){
                    			use_credit += Math.abs(credit_detail[j].amount)
                    		}
                    	}
                    }
                }
            }
            if(use_credit){
            	return 	credit_total - use_credit;
            } else{
            	return false
            }
    	},
    	generateUniqueId_barcode: function() {
            return new Date().getTime();
        },
        generate_unique_id: function() {
            var timestamp = new Date().getTime();
            return Number(timestamp.toString().slice(-10));
        },
        set_type_for_credit: function(type_for_credit) {
            this.set('type_for_credit', type_for_credit);
        },
        get_type_for_credit: function() {
            return this.get('type_for_credit');
        },
        set_client_name: function(client_name){
            this.client_name = client_name;
        },
        get_client_name: function(){
            return this.client_name;
        },
        set_change_amount_for_credit: function(change_amount_for_credit) {
            this.set('change_amount_for_credit', change_amount_for_credit);
        },
        get_change_amount_for_credit: function() {
            return this.get('change_amount_for_credit');
        },
        set_ledger_click: function(ledger_click){
    	    this.ledger_click = ledger_click;
    	},
    	get_ledger_click: function() {
    	    return this.ledger_click;
    	},
    	set_change_and_cash: function(change_and_cash) {
            this.change_and_cash = change_and_cash;
        },
        get_change_and_cash: function() {
            return this.change_and_cash;
        },
        set_use_credit: function(use_credit) {
            this.set('use_credit', use_credit);
        },
        get_use_credit: function() {
            return this.get('use_credit');
        },
        set_client_name: function(client_name){
            this.client_name = client_name;
        },
        get_client_name: function(){
            return this.client_name;
        },
        // Order History
        set_sequence:function(sequence){
        	this.set('sequence',sequence);
        },
        get_sequence:function(){
        	return this.get('sequence');
        },
        set_order_id: function(order_id){
            this.set('order_id', order_id);
        },
        get_order_id: function(){
            return this.get('order_id');
        },
        set_amount_paid: function(amount_paid) {
            this.set('amount_paid', amount_paid);
        },
        get_amount_paid: function() {
            return this.get('amount_paid');
        },
        set_amount_return: function(amount_return) {
            this.set('amount_return', amount_return);
        },
        get_amount_return: function() {
            return this.get('amount_return');
        },
        set_amount_tax: function(amount_tax) {
            this.set('amount_tax', amount_tax);
        },
        get_amount_tax: function() {
            return this.get('amount_tax');
        },
        set_amount_total: function(amount_total) {
            this.set('amount_total', amount_total);
        },
        get_amount_total: function() {
            return this.get('amount_total');
        },
        set_company_id: function(company_id) {
            this.set('company_id', company_id);
        },
        get_company_id: function() {
            return this.get('company_id');
        },
        set_date_order: function(date_order) {
            this.set('date_order', date_order);
        },
        get_date_order: function() {
            return this.get('date_order');
        },
        set_pos_reference: function(pos_reference) {
            this.set('pos_reference', pos_reference)
        },
        get_pos_reference: function() {
            return this.get('pos_reference')
        },
        set_user_name: function(user_id) {
            this.set('user_id', user_id);
        },
        get_user_name: function() {
            return this.get('user_id');
        },
        set_journal: function(statement_ids) {
            this.set('statement_ids', statement_ids)
        },
        get_journal: function() {
            return this.get('statement_ids');
        },
        set_delivery: function(is_delivery) {
            this.set('is_delivery', is_delivery);
        },
        get_delivery: function() {
            return this.get('is_delivery');
        },
        get_change: function(paymentline) {
            if (!paymentline) {
            	if(this.get_total_paid() > 0){
            		var change = this.get_total_paid() - this.get_total_with_tax();
            	}else{
            		var change = this.get_amount_return();
            	}
            } else {
                var change = -this.get_total_with_tax(); 
                var lines  = this.pos.get_order().get_paymentlines();
                for (var i = 0; i < lines.length; i++) {
                    change += lines[i].get_amount();
                    if (lines[i] === paymentline) {
                        break;
                    }
                }
            }
            return round_pr(Math.max(0,change), this.pos.currency.rounding);
        },
        export_as_JSON: function() {
        	var new_val = {};
            var orders = _super_Order.export_as_JSON.call(this);
            new_val = {
                old_order_id: this.get_order_id(),
                sequence: this.get_sequence(),
                pos_reference: this.get_pos_reference(),
                amount_due: this.get_due() ? this.get_due() : 0.00,
                credit_type: this.get_type_for_credit() || false,
            	change_amount_for_credit: this.get_change_amount_for_credit() || false,
        		is_delivery: this.get_delivery() || false,
        		credit_detail: this.get_credit_detail(),
            }
            $.extend(orders, new_val);
            return orders;
        },
        export_for_printing: function(){
        	var self =  this;
            var orders = _super_Order.export_for_printing.call(this);
            var last_paid_amt = 0;
            var currentOrderLines = this.get_orderlines();
            if(currentOrderLines.length > 0) {
            	_.each(currentOrderLines,function(item) {
            		if(self.pos.config.enable_credit &&
            				item.get_product().id == self.pos.config.prod_for_payment[0] ){
            			last_paid_amt = item.get_display_price()
            		}
                });
            }
            var total_paid_amt = this.get_total_paid()-last_paid_amt
            
            var new_val = {
            	reprint_payment: this.get_journal() || false,
            	ref: this.get_pos_reference() || false,
            	date_order: this.get_date_order() || false,
            	last_paid_amt: last_paid_amt || 0,
            	total_paid_amt: total_paid_amt || false,
            	amount_due: this.get_due() ? this.get_due() : 0.00,
            	old_order_id: this.get_order_id(),
            };
            $.extend(orders, new_val);
            return orders;
        },
        set_date_order: function(val){
        	this.set('date_order',val)
        },
        get_date_order: function(){
        	return this.get('date_order')
        },
        set_paying_order: function(val){
        	this.set('paying_order',val)
        },
        get_paying_order: function(){
        	return this.get('paying_order')
        },
    });

    var _super_orderlines = models.Orderline.prototype;
     models.Orderline = models.Orderline.extend({
        set_from_credit: function(from_credit) {
            this.from_credit = from_credit;
        },
        get_from_credit: function() {
            return this.from_credit;
        },
        export_as_JSON: function() {
            var lines = _super_orderlines.export_as_JSON.call(this);
            var new_attr = {
                from_credit:this.get_from_credit(),
            }
            $.extend(lines, new_attr);
            return lines;
        },
     });

	var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
           _super_posmodel.prototype.initialize.call(this,session,attributes);
           var  self = this;
           this.credit_amount = 0.00
        },
        fetch: function(model, fields, domain, ctx){
            this._load_progress = (this._load_progress || 0) + 0.05;
            this.chrome.loading_message(('Loading')+' '+model,this._load_progress);
            return new Model(model).query(fields).filter(domain).context(ctx).all()
        },
		load_server_data: function(){
			var self = this;
			var loaded = _super_posmodel.prototype.load_server_data.call(this);
			loaded = loaded.then(function(){
				if(self.config.enable_credit){
					var from_date = moment().format('YYYY-MM-DD')
					if(self.config.last_days){
						from_date = moment().subtract(self.config.last_days, 'days').format('YYYY-MM-DD');
					}
					self.domain_as_args = [['state','not in',['cancel']], ['create_date', '>=', from_date]];
					var params = {
						model: 'pos.order',
						method: 'ac_pos_search_read',
						args: [{'domain': self.domain_as_args}],
					}
					rpc.query(params, {async: false}).then(function(orders){
		                if(orders.length > 0){
		                	self.db.add_orders(orders);
		                    self.set({'pos_order_list' : orders});
		                }
		            });
				}
			});
			return loaded;
		},
		_save_to_server: function (orders, options) {
			var self = this;
			return _super_posmodel.prototype._save_to_server.apply(this, arguments)
			.then(function(server_ids){
				if(server_ids.length > 0 && self.config.enable_credit){
					var params = {
						model: 'pos.order',
						method: 'ac_pos_search_read',
						args: [{'domain': [['id','=',server_ids]]}],
					}
					rpc.query(params, {async: false}).then(function(orders){
		                if(orders.length > 0){
		                	orders = orders[0];
		                    var exist_order = _.findWhere(self.get('pos_order_list'), {'pos_reference': orders.pos_reference})
		                    if(exist_order){
		                    	_.extend(exist_order, orders);
		                    } else {
		                        if(orders){
		                            var orders_list = self.get('pos_order_list') || [];
                                    orders_list.push(orders);
                                }
		                    }
		                    var new_orders = _.sortBy(self.get('pos_order_list'), 'id').reverse();
		                    self.db.add_orders(new_orders);
		                    self.set({ 'pos_order_list' : new_orders });
		                }
		            });
				}
			});
		},
		get_customer_due: function(partner){
        	var self = this;
        	var domain = [];
            var amount_due = 0;
        	domain.push(['partner_id', '=', partner.id]);
        	var params = {
        		model: 'pos.order',
        		method: 'search_read',
        		domain: domain,
        	}
        	rpc.query(params, {async: false})
            .then(function(orders){
                if(orders){
                    var filtered_orders = orders.filter(function(o){return (o.amount_total - o.amount_paid) > 0})
                    for(var i = 0; i < filtered_orders.length; i++){
                        amount_due = amount_due + filtered_orders[i].amount_due;
                    }
                }
            })
            return amount_due;
        },
        // reload the list of partner, returns as a deferred that resolves if there were
        // updated partners, and fails if not
        load_new_partners: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
            var domain = [['customer','=',true],['write_date','>',this.db.get_partner_write_date()]];
            rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function(partners){
                	_.each(partners, function(partner){
                        if(self.db.partner_by_id[partner.id]){
                            var id = partner.id;
                            delete self.db.partner_by_id[partner.id]
                        }
                    });
                    if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(type,err){ def.reject(); });
            return def;
        },
	});

})