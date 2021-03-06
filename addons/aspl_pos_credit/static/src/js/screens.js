odoo.define('aspl_pos_credit.screens', function (require) {

	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var rpc = require('web.rpc');
	var utils = require('web.utils');
	var PopupWidget = require('point_of_sale.popups');
	var models = require('point_of_sale.models');
    var chrome = require('point_of_sale.chrome');
	var core = require('web.core');
	var QWeb = core.qweb;
	var round_pr = utils.round_precision;
	var _t = core._t;
    var DB = require('point_of_sale.DB');

    var PrintCreditStatement = screens.ActionButtonWidget.extend({
        template: 'PrintCreditStatement',
        button_click: function(){
            var self = this;
            if(this.pos.get_order().get_client() && this.pos.get_order().get_client().name){
                this.gui.show_popup('cash_inout_statement_popup');
                var order = this.pos.get_order();
                order.set_ledger_click(true);
            }else{
                self.gui.show_screen('clientlist');
            }
        },
    });
    screens.define_action_button({
        'name': 'creditledger',
        'widget': PrintCreditStatement,
        'condition': function(){
            return this.pos.config.enable_credit && this.pos.config.print_ledger;
        },
    });

     screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').unbind('click').click(function(){
                var order = self.pos.get_order();
                var partner = self.pos.get_order().get_client();
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(partner){
                    var params = {
                    model: 'account.invoice',
                    method: 'get_outstanding_info',
                    args: [partner.id]
                    }
                    rpc.query(params, {async: false}).then(function(res){
                        if(res){
                            partner['deposite_info'] = res;
                            _.each(res['content'], function(value){
                                  self.pos.amount = value['amount'];
                            });
                        }
                    });
                 }
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        },
    });

    screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            var order = self.pos.get_order();

            var partner = self.pos.get_order().get_client();
            this._super();
            self.pos.credit = false;
        },
        finalize_validation: function() {
            var self = this;
            var order = this.pos.get_order();
            var partner = this.pos.get_client();
            if(partner && partner.remaining_credit_amount && order.get_remaining_credit()){
            	partner.remaining_credit_amount = order.get_remaining_credit();
            }
            self._super();
        },
    });

    var AddMoneyToCreditButton = screens.ActionButtonWidget.extend({
        template: 'AddMoneyToCreditButton',
        button_click: function(){
            var self = this;
            var customer = self.pos.get_order().get_client()
            if(customer){
                self.gui.show_popup('AddMoneyToCreditPopup', {new_client: customer});
            }else{
                self.gui.show_screen('clientlist');
            }
        },
    });
    screens.define_action_button({
        'name': 'add_money_to_credit',
        'widget': AddMoneyToCreditButton,
        'condition': function(){
            return this.pos.config.enable_credit;
        },
    });

// Orders Button
	var ShowOrderList = screens.ActionButtonWidget.extend({
	    template : 'ShowOrderList',
	    button_click : function() {
	        self = this;
	        self.gui.show_screen('orderlist');
	    },
	});

	screens.define_action_button({
	    'name' : 'showorderlist',
	    'widget' : ShowOrderList,
	    'condition': function(){
            return this.pos.config.enable_credit;
        },
	});

    var CustomerCreditListScreenWidget = screens.ScreenWidget.extend({
	    template: 'CustomerCreditListScreenWidget',
	    get_customer_list: function(){
        	return this.pos.get('customer_credit_list');
        },
        show: function(options){
        	var self = this;
        	this.reloading_orders(this.get_cust_id());
            self.date = "all";
            var records = self.pos.get('customer_credit_list');
            this._super();
            self.render_list(records);
        	if(records){
                var partner = this.pos.db.get_partner_by_id(this.get_cust_id());
                self.display_client_details(partner);
        	}
            $('.back').click(function(){
                self.gui.show_screen('clientlist');
            })
            self.reload_orders();
            this.$('.print-ledger').click(function(){
                var order = self.pos.get_order();
                order.set_ledger_click(true);
                self.gui.show_popup('cash_inout_statement_popup');
            });
	        $('input#datepicker').datepicker({
           	    dateFormat: 'yy-mm-dd',
                autoclose: true,
                closeText: 'Clear',
                showButtonPanel: true,
                onSelect: function (dateText, inst) {
                	var date = $(this).val();
					if (date){
					    self.date = date;
					    self.render_list(self.get_customer_list());
					}
				},
				onClose: function(dateText, inst){
                    if( !dateText ){
                        self.date = "all";
                        self.render_list(self.get_customer_list());
                    }
                },
            }).focus(function(){
                var thisCalendar = $(this);
                $('.fa-times, .ui-datepicker-close').click(function() {
                    thisCalendar.val('');
                    self.date = "all";
                    self.render_list(self.get_customer_list());
                });
            });
            var old_goToToday = $.datepicker._gotoToday
            $.datepicker._gotoToday = function(id) {
                old_goToToday.call(this,id)
                this._selectDate(id)
            }
	    },
	    check_date_filter: function(records){
        	var self = this;
        	if(self.date !== "" && self.date !== "all"){
                var date_filtered_records = [];
            	for (var i=0; i<records.length;i++){
                    var date_record = $.datepicker.formatDate("yy-mm-dd",new Date(records[i].create_date));
            		if(self.date === date_record){
            			date_filtered_records.push(records[i]);
            		}
            	}
            	records = date_filtered_records;
            }
        	return records;
        },
	    render_list: function(records){
	        var self = this;
	        if(records && records.length > 0){
	            var contents = this.$el[0].querySelector('.credit-list-contents');
	            contents.innerHTML = "";
                if(self.date !== "" && self.date !== "all"){
	            	records = self.check_date_filter(records);
	            }
	            for(var i = 0, len = Math.min(records.length,1000); i < len; i++){
	                var self = this;
	                var record    = records[i];
	            	var clientline_html = QWeb.render('CreditlistLine',{widget: this, record:record});
	                var clientline = document.createElement('tbody');
	                clientline.innerHTML = clientline_html;
	                clientline = clientline.childNodes[1];
	                contents.appendChild(clientline);
	            }
        	} else{
        	    var contents = this.$el[0].querySelector('.credit-list-contents');
	            contents.innerHTML = "Record Not Found";
	            $("#pagination").hide();
        	}
        },
	    get_cust_id: function(){
            return this.gui.get_current_screen_param('cust_id');
        },
        reloading_orders: function(cust_id){
	    	var self = this;
	    	var partner = self.pos.db.get_partner_by_id(cust_id);
	    	var domain = []
	    	if(partner){
	    		if(partner.parent_id){
	    			partner = self.pos.db.get_partner_by_id(partner.parent_id[0]);
	    			domain.push(['partner_id','=',partner.id])
	    		} else{
	    			partner = self.pos.db.get_partner_by_id(cust_id)
	    			domain.push(['partner_id','=',partner.id])
	    		}
	    		var today = new Date();
	    		var end_date = moment(today).format('YYYY-MM-DD');
	    		var client_acc_id = partner.property_account_receivable_id;
	    		domain.push(['account_id','=',client_acc_id[0]],['date_maturity', '<=', end_date + " 23:59:59"]);
	    		var params = {
                    model: "account.move.line",
                    method: "search_read",
                    domain: domain,
                }
                rpc.query(params, {async: false})
                .then(function(records){
                	self.pos.set({'customer_credit_list' : records});
                    self.reload_orders();
                    return self.pos.get('customer_credit_list')
                });
	    	}
	    },
	    reload_orders: function(){
        	var self = this;
            var records = self.pos.get('customer_credit_list');
            this.search_list = []
            _.each(self.pos.partners, function(partner){
                self.search_list.push(partner.name);
            });
            _.each(records, function(record){
                self.search_list.push(record.display_name)
            });
            records = records.sort().reverse();
            this.render_list(records);
        },
        line_select: function(event,$line,id){
            var partner = this.pos.db.get_partner_by_id(id);
            this.$('.credit-list .lowlight').removeClass('lowlight');
                this.$('.credit-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                this.new_client = partner;
        },
        load_image_file: function(file, callback){
            var self = this;
            if (!file.type.match(/image.*/)) {
                this.gui.show_popup('error',{
                    title: _t('Unsupported File Format'),
                    body:  _t('Only web-compatible Image formats such as .png or .jpeg are supported'),
                });
                return;
            }

            var reader = new FileReader();
            reader.onload = function(event){
                var dataurl = event.target.result;
                var img     = new Image();
                img.src = dataurl;
                self.resize_image_to_dataurl(img,800,600,callback);
            };
            reader.onerror = function(){
                self.gui.show_popup('error',{
                    title :_t('Could Not Read Image'),
                    body  :_t('The provided file could not be read due to an unknown error'),
                });
            };
            reader.readAsDataURL(file);
        },
        display_client_details: function(partner, clickpos){
            var self = this;
            var contents = this.$('.credit-details-contents');
            contents.empty();
            var parent   = this.$('.order-list').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();
//            var partner = Number($('.client-line.highlight').attr('data-id'));
            contents.append($(QWeb.render('CustomerCreditDisplay',{widget:this, partner: partner})));
            var new_height   = contents.height();
            if(!this.details_visible){
                parent.height('-=' + new_height);
                if(clickpos < scroll + new_height + 20 ){
                    parent.scrollTop( clickpos - 20 );
                }else{
                    parent.scrollTop(parent.scrollTop() + new_height);
                }
            }else{
                parent.scrollTop(parent.scrollTop() - height + new_height);
            }
            this.details_visible = true;
        },
        partner_icon_url: function(id){
            return '/web/image?model=res.partner&id='+id+'&field=image_small';
        },
    });
    gui.define_screen({name:'customercreditlistscreen', widget: CustomerCreditListScreenWidget});

// Draft Button
	var SaveDraftButton = screens.ActionButtonWidget.extend({
	    template : 'SaveDraftButton',
	    button_click : function() {
	        var self = this;
            var selectedOrder = this.pos.get_order();
            selectedOrder.initialize_validation_date();
            var currentOrderLines = selectedOrder.get_orderlines();
            var orderLines = [];
            var client = selectedOrder.get_client();

//            Products added for draft are stored in "orderLines" list explicitly
            _.each(currentOrderLines,function(item) {
                return orderLines.push(item.export_as_JSON());
            });
            if (orderLines.length === 0) {
                return alert(_t('Please select product !'));
            } else {
            	if( this.pos.config.require_customer && !selectedOrder.get_client()){
            		self.gui.show_popup('error',{
                        message: _t('An anonymous order cannot be confirmed'),
                        comment: _t('Please select a client for this order. This can be done by clicking the order tab')
                    });
                    return;
            	}
                var credit = selectedOrder.get_total_with_tax() - selectedOrder.get_total_paid();
                this.pos.push_order(selectedOrder);
                self.gui.show_screen('receipt');
            }
	    },
	});

	screens.define_action_button({
	    'name' : 'savedraftbutton',
	    'widget' : SaveDraftButton,
	    'condition': function(){
            return this.pos.config.enable_credit;
        },
	});

	/* Order list screen */
	var OrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'OrderListScreenWidget',

	    init: function(parent, options){
	    	var self = this;
	        this._super(parent, options);
	        this.reload_btn = function(){
	        	$('.fa-refresh').toggleClass('rotate', 'rotate-reset');
	        	if($('#select_draft_orders').prop('checked')){
            		$('#select_draft_orders').click();
            	}
	        	self.reloading_orders();
	        };
	        if(this.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
            	self.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
	    },
	    events: {
	    	'click .button.back':  'click_back',
	    	'click .button.draft':  'click_draft',
	        'click .button.paid': 'click_paid',
	        'click .button.posted': 'click_posted',
	        'click #print_order': 'click_reprint',
	        'click #edit_order': 'click_edit_or_duplicate_order',
	        'click #re_order_duplicate': 'click_edit_or_duplicate_order',
	        'click #view_lines': 'click_view_lines',
	        'click #pay_due_amt': 'pay_order_due',
	        'keyup .searchbox input': 'search_order',
	    	'click .searchbox .search-clear': 'clear_search',
	    	'click .order-line td:not(.order_operation_button)': 'click_line',
	    },
	    filter:"all",
        date: "all",
        get_orders: function(){
        	return this.pos.get('pos_order_list');
        },
        click_back: function(){
        	this.gui.show_screen('products');
        },
        click_draft: function(event){
        	var self = this;
        	if($(event.currentTarget).hasClass('selected')){
        		$(event.currentTarget).removeClass('selected');
        		self.filter = "all";
    		}else{
        		self.$('.button.paid').removeClass('selected');
        		self.$('.button.posted').removeClass('selected');
    			$(event.currentTarget).addClass('selected');
    			var orders = self.pos.get_order();
        		self.filter = "draft";
    		}
    		self.render_list(self.get_orders());
        },
        click_paid: function(event){
        	var self = this;
        	if($(event.currentTarget).hasClass('selected')){
        		$(event.currentTarget).removeClass('selected');
        		self.filter = "all";
    		}else{
        		self.$('.button.draft').removeClass('selected');
        		self.$('.button.posted').removeClass('selected');
        		$(event.currentTarget).addClass('selected');
        		self.filter = "paid";
    		}
        	self.render_list(self.get_orders());
        },
        click_posted: function(event){
        	var self = this;
        	if($(event.currentTarget).hasClass('selected')){
        		$(event.currentTarget).removeClass('selected');
        		self.filter = "all";
    		}else{
    			self.$('.button.paid').removeClass('selected');
    			self.$('.button.draft').removeClass('selected');
    			$(event.currentTarget).addClass('selected');
        		self.filter = "done";
    		}
        	self.render_list(self.get_orders());
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
        get_journal_from_order: function(statement_ids){
	    	var self = this;
	    	var order = this.pos.get_order();
	    	var params = {
	    		model: 'account.bank.statement.line',
	    		method: 'search_read',
	    		domain: [['id', 'in', statement_ids]],
	    	}
	    	rpc.query(params, {async: false}).then(function(statements){
	    		if(statements.length > 0){
	    			var order_statements = []
	    			_.each(statements, function(statement){
	    				if(statement.amount > 0){
	    					order_statements.push({
	    						amount: statement.amount,
	    						journal: statement.journal_id[1],
	    					})
	    				}
	    			});
	    			order.set_journal(order_statements);
	    		}
	    	});
	    },
	    get_orderlines_from_order: function(line_ids){
	    	var self = this;
	    	var order = this.pos.get_order();
	    	var orderlines = false;
	    	var params = {
	    		model: 'pos.order.line',
	    		method: 'search_read',
	    		domain: [['id', 'in', line_ids]],
	    	}
	    	rpc.query(params, {async: false}).then(function(order_lines){
	    		if(order_lines.length >= 0){
	    			orderlines = order_lines;
	    		}
	    	});
	    	return orderlines
	    },
//	    Click on reprint
        click_reprint: function(event){
        	var self = this;
        	var selectedOrder = this.pos.get_order();
        	var order_id = parseInt($(event.currentTarget).data('id'));

        	self.clear_cart();
        	selectedOrder.set_client(null);
        	var result = self.pos.db.get_order_by_id(order_id);
        	if (result && result.lines.length > 0) {
        		if (result.partner_id && result.partner_id[0]) {
                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    if(partner){
                    	selectedOrder.set_client(partner);
                    }
                }
        		selectedOrder.set_amount_paid(result.amount_paid);
                selectedOrder.set_amount_return(Math.abs(result.amount_return));
                selectedOrder.set_amount_tax(result.amount_tax);
                selectedOrder.set_amount_total(result.amount_total);
                selectedOrder.set_company_id(result.company_id[1]);
                selectedOrder.set_date_order(result.date_order);
                selectedOrder.set_client(partner);
                selectedOrder.set_pos_reference(result.pos_reference);
                selectedOrder.set_user_name(result.user_id && result.user_id[1]);
                selectedOrder.set_date_order(result.date_order);
                if(result.statement_ids.length > 0){
                	self.get_journal_from_order(result.statement_ids);
                }
                if(result.lines.length > 0){
                	var order_lines = self.get_orderlines_from_order(result.lines);
                	if(order_lines.length > 0){
	                	_.each(order_lines, function(line){
		    				var product = self.pos.db.get_product_by_id(Number(line.product_id[0]));
		    				if(product){
		    					selectedOrder.add_product(product, {
		    						quantity: line.qty,
		    						discount: line.discount,
		    						price: line.price_unit,
		    					})
		    				}
		    			})
		    			var prd = self.pos.db.get_product_by_id(self.pos.config.prod_for_payment[0]);
                   		if(prd && result.amount_due > 0){
                     		var paid_amt = result.amount_total - result.amount_due;
                     		selectedOrder.add_product(prd,{'price':-paid_amt});
                     	}
                	}
                }
                selectedOrder.set_order_id(order_id);
                self.gui.show_screen('receipt');
        	}
        },
//        Click on eye
        click_view_lines: function(event){
        	var self = this;
        	var order_id = parseInt($(event.currentTarget).data('id'));
            var order = this.pos.get_order();
            var result = self.pos.db.get_order_by_id(order_id);
            if(result.lines.length > 0){
            	var order_lines = self.get_orderlines_from_order(result.lines);
            	if(order_lines){
            		self.gui.show_popup('product_popup', {
            			order_lines: order_lines,
            			order_id: order_id,
            			state: result.state,
            			order_screen_obj: self,
            		});
            	}
            }
        },
//        Click on Edit
        click_edit_or_duplicate_order: function(event){
        	var self = this;
        	var order_id = parseInt($(event.currentTarget).data('id'));
            var selectedOrder = this.pos.get_order();
            var result = self.pos.db.get_order_by_id(order_id);
            if(result.lines.length > 0){
                // if edit operation
            	if($(event.currentTarget).data('operation') === "edit"){
	            	if(result.state == "paid"){
	                	alert(_t("Sorry, This order is paid State"));
	                	return
	                }
	                if(result.state == "done"){
	                	alert(_t("Sorry, This Order is Done State"));
	                	return
	                }
            	}
                self.clear_cart();
            	selectedOrder.set_client(null);
            	// if partner and partner_id
            	if (result.partner_id && result.partner_id[0]) {
                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    if(partner){
                    	selectedOrder.set_client(partner);
                    }
                }
                // if not reorder operation
            	if($(event.currentTarget).data('operation') !== _t("reorder")){
	           	 	selectedOrder.set_pos_reference(result.pos_reference);
	           	 	selectedOrder.set_order_id(order_id);
	           	 	selectedOrder.set_sequence(result.name);
            	}
	           	if(result.lines.length > 0){
	            	var order_lines = self.get_orderlines_from_order(result.lines);
	            	if(order_lines.length > 0){
		               	_.each(order_lines, function(line){
			    			var product = self.pos.db.get_product_by_id(Number(line.product_id[0]));
			    			if(product){
			    				selectedOrder.add_product(product, {
			    					quantity: line.qty,
			    					discount: line.discount,
			    					price: line.price_unit,
			    				})
			    			}
			    		})
	            	}
	            }
	           	self.gui.show_screen('products');
	           	var prd = self.pos.db.get_product_by_id(self.pos.config.prod_for_payment[0]);
	           	if(prd && result.amount_due > 0){
                    var paid_amt = result.amount_total - result.amount_due;
//                    Dummy Product added to Cart
                    selectedOrder.add_product(prd,{'price':-paid_amt});
                }
            }
        },
        click_line: function(event){
        	var self = this;
        	var order_id = parseInt($(event.currentTarget).parent().data('id'));
            self.gui.show_screen('orderdetail', {'order_id': order_id});
        },
	    pay_order_due: function(event, order_id){
	        var self = this;
	        var order_id = event ? parseInt($(event.currentTarget).data('id')) : order_id;
	        var selectedOrder = this.pos.get_order();
	        var result = self.pos.db.get_order_by_id(order_id);
	        if(!result){
	        	var params = {
	        		model: 'pos.order',
	        		method: 'search_read',
	        		domain: [['id', '=', order_id], ['state', 'not in', ['draft']]]
	        	}
	        	rpc.query(params, {async: false}).then(function(order){
	                if(order && order[0])
	                    result = order[0]
	            });
	        }
	        if(result){
	            if(result.state == "paid"){
	                alert(_t("Sorry, This order is paid State"));
	                return
	            }
	            if(result.state == "done"){
	                alert(_t("Sorry, This Order is Done State"));
	                return
	            }
	            if (result && result.lines.length >= 0) {
	            	self.clear_cart();
	            	selectedOrder.set_client(null);
	            	if (result.partner_id && result.partner_id[0]) {
	                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
	                    if(partner){
	                    	selectedOrder.set_client(partner);
	                    }
	                }
	                selectedOrder.set_pos_reference(result.pos_reference);
	                selectedOrder.set_paying_order(true);
	                selectedOrder.set_order_id(order_id);
	                selectedOrder.set_sequence(result.name);
	                selectedOrder.set_delivery(result.is_delivery);
	                if(result.lines.length >= 0){
		            	var order_lines = self.get_orderlines_from_order(result.lines);
		            	if(order_lines.length >= 0){
			               	_.each(order_lines, function(line){
				    			var product = self.pos.db.get_product_by_id(Number(line.product_id[0]));
				    			if(product){
				    				selectedOrder.add_product(product, {
				    					quantity: line.qty,
				    					discount: line.discount,
				    					price: line.price_unit,
				    				})
				    			}
				    		});
			               	var prd = self.pos.db.get_product_by_id(self.pos.config.prod_for_payment[0]);
	                        if(prd && result.amount_due){
	                            var paid_amt = result.amount_total - result.amount_due;
	                            selectedOrder.add_product(prd,{'price':-paid_amt});
	                        }
                            self.gui.show_screen('payment');
	                        if(result.picking_id){
                                $('.deliver_items').hide();
                            }
	                        if(result.amount_due == 0){
	                            selectedOrder.set_amount_paid(result.amount_paid)
	                        }
		            	}
		            }
	            }
	    	}
	    },
//	    Shows All orders - Paid and Unpaid
	    show: function(){
        	var self = this;
	        this._super();
	        if($('#select_draft_orders').prop('checked')){
        		$('#select_draft_orders').click();
        	}
	        this.reload_orders();
	        $('input#datepicker').datepicker({
           	    dateFormat: 'yy-mm-dd',
                autoclose: true,
                closeText: 'Clear',
                showButtonPanel: true,
                onSelect: function (dateText, inst) {
                	var date = $(this).val();
					if (date){
					    self.date = date;
					    self.render_list(self.get_orders());
					}
				},
				onClose: function(dateText, inst){
                    if( !dateText ){
                        self.date = "all";
                        self.render_list(self.get_orders());
                    }
                },
            }).focus(function(){
                var thisCalendar = $(this);
                $('.ui-datepicker-close').click(function() {
                    thisCalendar.val('');
                    self.date = "all";
                    self.render_list(self.get_orders());
                });
            });
            var old_goToToday = $.datepicker._gotoToday
            $.datepicker._gotoToday = function(id) {
                old_goToToday.call(this,id)
                this._selectDate(id)
            }
	    },
//	    Search Order
	    search_order: function(event){
	    	var self = this;
	    	var search_timeout = null;
	    	clearTimeout(search_timeout);
            var query = $(event.currentTarget).val();
            search_timeout = setTimeout(function(){
                self.perform_search(query,event.which === 13);
            },70);
	    },
//	    Search Order
	    perform_search: function(query, associate_result){
	        var self = this;
            if(query){
                if (associate_result){
                    var domain = ['|', '|',['partner_id', 'ilike', query], ['name', 'ilike', query], ['pos_reference', 'ilike', query]];
                    var params = {
                    	model: 'pos.order',
                    	method: 'search_read',
                    	domain: [domain],
                    }
                    rpc.query(params, {async: false}).then(function(orders){
                    	self.render_list(orders);
                    })
                } else {
                    var orders = this.pos.db.search_order(query);
                    self.render_list(orders);
                }
            }else{
                var orders = self.pos.get('pos_order_list');
                this.render_list(orders);
            }
        },
        clear_search: function(){
            var orders = this.pos.get('pos_order_list');
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        check_filters: function(orders){
        	var self = this;
        	var filtered_orders = false;
        	if(self.filter !== "" && self.filter !== "all"){
	            filtered_orders = $.grep(orders,function(order){
                    if((order.amount_total !== 0 && order.state !== 'draft') || (order.amount_total > 0 && order.state == 'draft')){
                        return order.state === self.filter;
                    }
	            });
            }
        	return filtered_orders || orders;
        },
        check_date_filter: function(orders){
        	var self = this;
        	var date_filtered_orders = [];
        	if(self.date !== "" && self.date !== "all"){

            	for (var i=0; i<orders.length;i++){
                    var date_order = $.datepicker.formatDate("yy-mm-dd",new Date(orders[i].date_order));
            		if(self.date === date_order){
            			date_filtered_orders.push(orders[i]);
            		}
            	}
            }
        	return date_filtered_orders;
        },
//        Render Order List
        render_list: function(orders){
            var self = this;
        	if(orders){
	            var contents = this.$el[0].querySelector('.order-list-contents');
	            contents.innerHTML = "";
	            var temp = [];
	            orders = self.check_filters(orders);
	            if(self.date !== "" && self.date !== "all"){
	            	orders = self.check_date_filter(orders);
	            }
	            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
	                var order    = orders[i];
	                order.amount_total = parseFloat(order.amount_total).toFixed(2);
	            	var clientline_html = QWeb.render('OrderlistLine',{widget: this, order:order});
	                var clientline = document.createElement('tbody');
	                clientline.innerHTML = clientline_html;
	                clientline = clientline.childNodes[1];
	                contents.appendChild(clientline);
	            }
	            $("table.order-list").simplePagination({
					previousButtonClass: "btn btn-danger",
					nextButtonClass: "btn btn-danger",
					previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
					nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
					perPage:self.pos.config.record_per_page > 0 ? self.pos.config.record_per_page : 10
				});
        	}
        },
        reload_orders: function(){
        	var self = this;
            var orders = self.pos.get('pos_order_list');
            this.search_list = []
            _.each(self.pos.partners, function(partner){
                self.search_list.push(partner.name);
            });
            _.each(orders, function(order){
                self.search_list.push(order.display_name, order.pos_reference)
            });
            this.render_list(orders);
        },
        reloading_orders: function(){
	    	var self = this;
	    	var params = {
				model: 'pos.order',
				method: 'ac_pos_search_read',
				args: [{'domain': this.pos.domain_as_args}],
			}
			return rpc.query(params, {async: false}).then(function(orders){
                if(orders.length > 0){
                	self.pos.db.add_orders(orders);
                    self.pos.set({'pos_order_list' : orders});
                    self.reload_orders();
                }
            }).fail(function (type, error){
                if(error.code === 200 ){ // Business Logic Error, not a connection problem
                   self.gui.show_popup('error-traceback',{
                        'title': error.data.message,
                        'body':  error.data.debug
                   });
                }
            });
	    },
	    renderElement: function(){
	    	var self = this;
	    	self._super();
	    	self.el.querySelector('.button.reload').addEventListener('click',this.reload_btn);
	    },
	});
	gui.define_screen({name:'orderlist', widget: OrderListScreenWidget});

	screens.PaymentScreenWidget.include({
	    events:{
	        'click .credit_assign':'credit_assign'
	    },
	    credit_assign: function(e){
            $(".account_payment_btn").html("");
	        var self = this;
	        var order = self.pos.get_order();
	        var partner = order.get_client();
	        var add_class = false;
            if($(e.currentTarget).hasClass('account_pay')){
                add_class = false;
                $(e.currentTarget).removeClass('account_pay');
                var lines = self.pos.get_order().get_orderlines()
                var new_amount = Number($(e.currentTarget).attr('use_amt'));
                var order_amount = order.get_total_with_tax();
                var to_be_remove = false
                var credit_detail = order.get_credit_detail();
                var journal_id = Number($(e.currentTarget).attr('journal_id'));
                for (var i=0;i<lines.length;i++){
                	if(lines[i].product.id == self.pos.config.prod_for_payment[0]){
                		for (var j=0;j<credit_detail.length;j++){
                			if(lines[i].price == (-credit_detail[j].amount)){
                    			to_be_remove = lines[i].id
                    			break
                    		}
                		}
                	}
                }
                for(var i=0;i<credit_detail.length;i++){
                	if(credit_detail[i].journal_id == journal_id){
                		credit_detail.splice(i, 1);

                	}
                }
                 if(order.get_orderline(to_be_remove)){
                     order.remove_orderline(order.get_orderline(to_be_remove));
                 }
                var pos_total_amount = 0.00
                var order_details =  order.get_credit_detail()
                 _.each(order_details,function(order_detail) {
                    pos_total_amount += order_detail.amount
                });
                 self.pos.credit_amount = pos_total_amount;
                 var tabs = QWeb.render('FromCredit',{widget:self});
                 $('.foreign_infoline').html(tabs);
            }else{
                $(e.currentTarget).addClass('account_pay');
                var journal = $(e.currentTarget).attr('journal');
                var journal_id = Number($(e.currentTarget).attr('journal_id'));
                var amount = Number($(e.currentTarget).attr('amt'));
                var order_amount = order.get_total_with_tax();
                var prd = self.pos.db.get_product_by_id(self.pos.config.prod_for_payment[0]);
                var lines = self.pos.get_order().get_orderlines()
                self.pos.credit = true;
                self.pos.cmp_journal_id = journal_id;
                if(prd && order_amount != 0.00){
                      if(order_amount < amount){
                        var paid_amt =  order_amount;
                      } else{
                            var paid_amt = amount;
                      }
//                      if(lines.length > 0){
//                    	  _.each(lines,function(line){
//                    		  if(line.product.id == prd.id){
//                    			  order.remove_orderline(line)
//                    		  }
//                    	  });
//                      }
                      order.add_product(prd,{'price':-paid_amt});
                      $(e.currentTarget).attr('use-amt',-paid_amt);
                       var select_line = order.get_selected_orderline();
                       if(select_line){
                            select_line.set_from_credit(true);
                            var credit_info = {
                                'partner_id':partner.id,
                                'amount':paid_amt,
                                'journal':journal,
                                'journal_id':journal_id
                            }
                            order.set_credit_detail(credit_info);
                       }
                }
                var pos_total_amount = 0.00
                var order_details =  order.get_credit_detail()
                _.each(order_details,function(order_detail) {
                    pos_total_amount += order_detail.amount
                });
                self.pos.credit_amount = pos_total_amount;
                var tabs = QWeb.render('FromCredit',{widget:self});
                this.$('.foreign_infoline').html(tabs);
            }
            var p_line = order.get_paymentlines(); 
	        if(p_line.length > 0){
	        	self.pos.gui.screen_instances.payment.render_paymentlines()
	        }
	    },
	    init: function(parent, options) {
    		var self = this;
            this._super(parent, options);
            this.use_credit = function(event){
                var order = self.pos.get_order();
                if(order.get_due() <= 0){
                    return;
                }
                order.set_use_credit(!order.get_use_credit());
                if (order.get_use_credit()) {
                    if(order.get_client()){
                        var params = {
                            model: "res.partner",
                            method: "search_read",
                            domain: [['id', '=', order.get_client().id]],
                            fields:['remaining_credit_amount']
                        }
                        rpc.query(params, {async: false})
                        .then(function(results){
                            if(results && results[0]){
                            	if(results[0].remaining_credit_amount <= 0){
                            		return
                            	}
                            	$('div.js_use_credit').addClass('highlight');
                            	var result = results[0];
                                var price = 0;
                                if(order.get_total_with_tax() < result.remaining_credit_amount){
                                    var rem = self.pos.get_order().get_due();
                                    price = rem || order.get_total_with_tax() * -1;
                                    order.set_type_for_credit('return');
                                    self.click_paymentmethods_by_journal(self.pos.config.pos_journal_id[0]);
                                }else if(order.get_total_with_tax() >= result.remaining_credit_amount){
                                    order.set_type_for_credit('change');
                                    var rem_due = self.pos.get_order().get_due();
                                    self.click_paymentmethods_by_journal(self.pos.config.pos_journal_id[0]);
                                    price = Math.min(rem_due,Math.abs(result.remaining_credit_amount * -1));
                                }else{
                                    order.set_type_for_credit('change');
                                }
                                self.renderElement();
                            }
                        });
                    }else {
                        alert(_t('Please select a customer to use Credit !'));
                    }
                }else {
                    $('.js_use_add_paymentlinecredit').removeClass('highlight');
                    self.renderElement();
                }
    	    };
    	},
    	show: function(){
    	    var self = this;
    	    var order = self.pos.get_order();
    	    var partner = self.pos.get_order().get_client();
    	    this._super();
    	    order.set_credit_mode(false)
            if(order && order.get_client()){
                $('.js_use_credit').show();
                this.remaining_balance = order.get_client().remaining_credit_amount;
                self.renderElement();
            }else{
                $('.js_use_credit').hide();
            }
    	},
        partial_payment: function() {
            var self = this;
        	var currentOrder = this.pos.get_order();
        	var client = currentOrder.get_client() || false;
        	var partner = this.pos.get_client();
            if(partner && partner.remaining_credit_amount && currentOrder.get_remaining_credit()){
            	partner.remaining_credit_amount = currentOrder.get_remaining_credit();
            }
        	if(currentOrder.get_total_with_tax() > currentOrder.get_total_paid() && currentOrder.get_total_paid() > 0){
        		var credit = currentOrder.get_total_with_tax() - currentOrder.get_total_paid();
        		this.finalize_validation();
        	}
        },
        renderElement: function() {
            var self = this;
            var currentOrder = self.pos.get_order();
            this._super();
            $('.delivery_check').click(function(){
                $('.delivery_check').find('i').toggleClass('fa fa-toggle-on fa fa-toggle-off');
            })
            this.$('#partial_pay').click(function(){
                var value = $('.delivery_check').find('i').hasClass('fa-toggle-on')
                if(value){
                    currentOrder.set_delivery(value)
                }
                self.partial_payment();
            });
            if(self.pos.config.enable_credit && self.pos.get_order() && self.pos.get_order().get_client()){
         	   self.el.querySelector('.js_use_credit').addEventListener('click', this.use_credit);
            }
        },
        order_changes: function(){
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var total = order ? order.get_total_with_tax() : 0;
            if(!order){
            	return
            } else if(order.get_due() == 0 || order.get_due() == total ){
            	self.$('#partial_pay').removeClass('highlight');
            } else {
            	self.$('#partial_pay').addClass('highlight');
            }
        },
        click_back: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        if(order.get_credit_detail() && order.get_credit_detail()[0]){
                this.gui.show_popup('confirm',{
                    title: _t('Discard Order'),
                    body:  _t('Do you want to discard the Order'),
                    confirm: function() {
                        order.finalize();
                    },
                });
	        } else {
	            self._super();
	        }
	    },
	    click_invoice: function(){
            var self = this;
	        var order = this.pos.get_order();
	        if(!order.get_paying_order()){
	            this._super();
	        }
	    },
	    click_set_customer: function(){
	        var self = this;
	        var order = this.pos.get_order();
	        if(!order.get_paying_order()){
	            self._super();
	        }
	    },
        validate_order: function(force_validation) {
            var self = this;
            var currentOrder = self.pos.get_order();
            if(self.pos.get_client()){
                $('.delivery_check').click(function(){
                    $('.delivery_check').find('i').toggleClass('fa fa-toggle-on fa fa-toggle-off');
                })
                var value = $('.delivery_check').find('i').hasClass('fa-toggle-on')
                if(value){
                    currentOrder.set_delivery(value)
                }
                self._super(self, force_validation);
//                if(currentOrder.get_change() && self.pos.config.enable_credit){
//                    self._super(self, force_validation);
//                }else{
//                    self._super(self, force_validation);
//                }
    		}else if((this.pos.get_order().get_total_with_tax() < 0) && this.pos.get_order().get_paymentlines().length == 0){
                return alert(_t('Please select a journal.'));
            }else if (this.order_is_valid(force_validation)) {
                this.finalize_validation();
            }else{
                self._super(self, force_validation);
            }
        },
        click_paymentmethods: function(id) {
            var cashregister = null;
            for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
                if ( this.pos.cashregisters[i].journal_id[0] === id ){
                    cashregister = this.pos.cashregisters[i];
                    break;
                }
            }
            this.pos.get_order().add_paymentline( cashregister );
            this.reset_input();
            this.render_paymentlines();
        },
        click_paymentmethods_by_journal: function(id) {
            var cashregister = null;
            for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
                if ( this.pos.cashregisters[i].journal_id[0] === id ){
                    cashregister = this.pos.cashregisters[i];
                    break;
                }
            }
            this.pos.get_order().add_paymentline_by_journal( cashregister );
            this.reset_input();
            this.render_paymentlines();
        },
    });

    var OrderDetailScreenWidget = screens.ScreenWidget.extend({
	    template: 'OrderDetailScreenWidget',
        show: function(){
            var self = this;
            self._super();
            var order = self.pos.get_order();
            var params = order.get_screen_data('params');
            var order_id = false;
            if(params){
                order_id = params.order_id;
            }
            if(order_id){
                self.clicked_order = self.pos.db.get_order_by_id(order_id)
                if(!self.clicked_order){
                	var detail_param = {
                		model: 'pos.order',
                		method: 'search_read',
                		domain: [['id', '=', order_id]],
                	}
                    rpc.query(detail_param, {async: false}).then(function(order){
                        if(order && order[0]){
                            self.clicked_order = order[0];
                        }
                    })
                }
            }
            this.renderElement();
            this.$('.back').click(function(){
                self.gui.back();
                if(params.previous){
                    self.pos.get_order().set_screen_data('previous-screen', params.previous);
                    if(params.partner_id){
                        $('.client-list-contents').find('.client-line[data-id="'+ params.partner_id +'"]').click();
                        $('#show_client_history').click();
                    }
                }
            });
            if(self.clicked_order){
                this.$('.pay').click(function(){
                	self.pos.gui.screen_instances.orderlist.pay_order_due(false, order_id)
                });
                var contents = this.$('.order-details-contents');
                contents.append($(QWeb.render('OrderDetails',{widget:this, order:self.clicked_order})));
                var params = {
                	model: 'account.bank.statement.line',
                	method: 'search_read',
                	domain: [['pos_statement_id', '=', order_id]],
                }
                rpc.query(params, {async: false}).then(function(statements){
                    if(statements){
                        self.render_list(statements);
                    }
                });
            }
        },
        render_list: function(statements){
        	if(statements){
	            var contents = this.$el[0].querySelector('.paymentline-list-contents');
	            contents.innerHTML = "";
	            for(var i = 0, len = Math.min(statements.length,1000); i < len; i++){
	                var statement = statements[i];
	                var paymentline_html = QWeb.render('PaymentLines',{widget: this, statement:statement});
	                var paymentline = document.createElement('tbody');
	                paymentline.innerHTML = paymentline_html;
	                paymentline = paymentline.childNodes[1];
	                contents.append(paymentline);
	            }
        	}
        },
	});
	gui.define_screen({name:'orderdetail', widget: OrderDetailScreenWidget});

	screens.ClientListScreenWidget.include({
        show: function(){
            var self = this;
            var order = this.pos.get_order();
            this._super();

            this.$('.credit').click(function(){
                self.pos.get('customer_credit_list');
                var selected_line = Number($('.client-line.highlight').attr('data-id')) || self.new_client.id || self.old_client.id;
                self.gui.show_screen('customercreditlistscreen', {cust_id: selected_line});
                var records = self.pos.get('customer_credit_list');
                self.render_list(records)
            });
            this.$('.add-money-button').click(function() {
                self.save_changes();
                var selected_line = Number($('.client-line.highlight').attr('data-id')) || self.new_client.id || self.old_client.id;
                if(selected_line){
                    var customer = self.pos.db.get_partner_by_id(selected_line)
                    if(customer){
                        self.gui.show_popup('AddMoneyToCreditPopup', {new_client: customer});
                    }
                }
            });
            this.$('.back').click(function(){
                self.gui.show_screen('products');
            });
            this.$('.print-ledger').click(function(){
                var pos_session_id = self.pos.pos_session.id;
                var order = self.pos.get_order();
                order.set_ledger_click(true);
                self.gui.show_popup('cash_inout_statement_popup');
            });
            var $show_customers = $('#show_customers');
            var $show_client_history = $('#show_client_history');
            if (this.pos.get_order().get_client() || this.new_client) {
                $show_client_history.removeClass('oe_hidden');
            }
            $show_customers.off().on('click', function(e){
                $('.client-list').removeClass('oe_hidden');
                $('.customer_history').addClass('oe_hidden')
                $show_customers.addClass('oe_hidden');
                $show_client_history.removeClass('oe_hidden');
            })
        },
        save_changes: function(){
            var order = this.pos.get_order();
            if( this.has_client_changed() ){
                var default_fiscal_position_id = _.findWhere(this.pos.fiscal_positions, {'id': this.pos.config.default_fiscal_position_id[0]});
                if ( this.new_client ) {
                    order.fiscal_position = _.findWhere(this.pos.fiscal_positions, {'id': this.new_client.property_account_position_id[0]});
                    order.set_pricelist(_.findWhere(this.pos.pricelists, {'id': this.new_client.property_product_pricelist[0]}) || this.pos.default_pricelist);
                } else {
                    order.fiscal_position = default_fiscal_position_id;
                    order.set_pricelist(this.pos.default_pricelist);
                }

                order.set_client(this.new_client);
            }
        },
        hide: function () {
            this._super();
            this.new_client = null;
        },
        has_client_changed: function(){
            if( this.old_client && this.new_client ){
                return this.old_client.id !== this.new_client.id;
            }else{
                return !!this.old_client !== !!this.new_client;
            }
        },
        toggle_save_button: function(){
            var self = this;
            this._super();
            var $show_customers = this.$('#show_customers');
            var $show_client_history = this.$('#show_client_history');
            var $customer_history = this.$('#customer_history');
            var client = this.new_client || this.pos.get_order().get_client();
            if (this.editing_client) {
                $show_customers.addClass('oe_hidden');
                $show_client_history.addClass('oe_hidden');
            } else {
                if(client){
                    $show_client_history.removeClass('oe_hidden');
                    $show_client_history.off().on('click', function(e){
                        self.render_client_history(client);
                        $('.client-list').addClass('oe_hidden');
                        $customer_history.removeClass('oe_hidden');
                        $show_client_history.addClass('oe_hidden');
                        $show_customers.removeClass('oe_hidden');
                    });
                } else {
                    $show_client_history.addClass('oe_hidden');
                    $show_client_history.off();
                }
            }
            var $credit_button = this.$('.button.credit');
            if (this.editing_client) {
                $credit_button.addClass('oe_hidden');
                return;
            } else if( this.new_client ){
                if( !this.old_client){
                    $credit_button.text(_t('Credit History'));
                }else{
                    $credit_button.text(_t('Credit History'));
                }
            }else{
                $credit_button.text(_t('Credit History'));
            }
            $credit_button.toggleClass('oe_hidden',!this.has_client_changed());


            var $add_money_button = this.$('.button.add-money-button');
            if (this.editing_client) {
                $add_money_button.addClass('oe_hidden');
                return;
            } else if( this.new_client ){
                if( !this.old_client){
                    $add_money_button.text(_t('Add Credit'));
                }else{
                    $add_money_button.text(_t('Add Credit'));
                }
            }else{
                $add_money_button.text(_t('Add Credit'));
            }
            $add_money_button.toggleClass('oe_hidden',!this.has_client_changed());

        },
        _get_customer_history: function(partner){
        	var self = this;
        	var domain = self.pos.domain_as_args.slice();
        	domain.push(['partner_id', '=', partner.id]);
        	var params = {
        		model: 'pos.order',
        		method: 'search_read',
        		domain: domain,
        	}
        	rpc.query(params, {async: false})
            .then(function(orders){
                if(orders){
                     var filtered_orders = orders.filter(function(o){
                    	 return (o.amount_total - o.amount_paid) > 0
                	 });
                     partner['history'] = filtered_orders
                }
            })
        },
        render_client_history: function(partner){
            var self = this;
            var contents = this.$el[0].querySelector('#client_history_contents');
            contents.innerHTML = "";
            self._get_customer_history(partner)
            if(partner.history){
                for (var i=0; i < partner.history.length; i++){
                    var history = partner.history[i];
                    var history_line_html = QWeb.render('ClientHistoryLine', {
                        partner: partner,
                        order: history,
                        widget: self,
                    });
                    var history_line = document.createElement('tbody');
                    history_line.innerHTML = history_line_html;
                    history_line = history_line.childNodes[1];
                    history_line.addEventListener('click', function(e){
                        var order_id = $(this).data('id');
                        if(order_id){
                        	var previous = self.pos.get_order().get_screen_data('previous-screen');
                            self.gui.show_screen('orderdetail', {
                                order_id: order_id,
                                previous: previous,
                                partner_id: partner.id
                            });
                        }
                    })
                    contents.appendChild(history_line);
                }
            }
        },
        render_payment_history: function(){
            var self = this;
            var $client_details_box = $('.client-details-box');
            $client_details_box.addClass('oe_hidden');
        }
	});

});