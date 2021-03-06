odoo.define('aspl_pos_credit.popups', function (require) {
	"use strict";

	var gui = require('point_of_sale.gui');
	var keyboard = require('point_of_sale.keyboard').OnscreenKeyboardWidget;
	var rpc = require('web.rpc');
	var chrome = require('point_of_sale.chrome');
	var utils = require('web.utils');
	var PopupWidget = require('point_of_sale.popups');
    var DB = require('point_of_sale.DB');
	var core = require('web.core');
	var QWeb = core.qweb;
	var round_pr = utils.round_precision;
	var _t = core._t;

    var PrintCashInOutStatmentPopup = PopupWidget.extend({
        template: 'PrintCashInOutStatmentPopup',
        show: function(options){
        	var self = this;
        	self._super(options);
        	$('.start-date input').focus();
        },
        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();
            var start_date = $('.start-date input').val();
            var end_date = $('.end-date input').val();
            var customer_id = self.pos.gui.screen_instances.customercreditlistscreen.get_cust_id()
            customer_id = customer_id ? customer_id : self.pos.get_client().id;
            var partner = self.pos.db.get_partner_by_id(customer_id);
        	if(partner.parent_id){
    			partner = self.pos.db.get_partner_by_id(partner.parent_id[0]);
    		} else{
    			partner = self.pos.db.get_partner_by_id(customer_id)
    		}
            var account_id = partner.property_account_receivable_id;
            if(start_date > end_date){
                alert("Start date should not be greater than end date");
                return
            }
            if(start_date && end_date){
                var params = {
                    model: "account.move.line",
                    method: "search_read",
                    domain: [['date_maturity', '>=', start_date  + " 00:00:00"],['date_maturity', '<=', end_date + " 23:59:59"],
                             ['partner_id','=',partner.id],['account_id','=',account_id[0]]],
                }
                rpc.query(params, {async: false})
                .then(function(vals){
                    if(vals){
                        if(partner && vals.length > 0){
                            self.gui.show_screen('receipt');
                            partner = self.pos.db.get_partner_by_id(customer_id);
                            $('.pos-receipt-container', this.$el).html(QWeb.render('AddedCreditStatement',{
                                widget: self,
                                order: order,
                                move_line:vals,
                                partner:partner
                            }));
                        } else{
                            return
                        }
                    }
                });
            }
            else if(start_date == "" && end_date !== ""){
                $('.start-date input').css({'border-style': 'solid','border-width': '1px',
                    'border-color': 'rgb(255, 0, 0)'});
                $('.end-date input').css({'border-color': 'rgb(224,224,224)'});
            }else if(end_date == "" && start_date !== ""){
                $('.end-date input').css({'border-style': 'solid','border-width': '1px',
                    'border-color': 'rgb(255, 0, 0)'});
                $('.start-date input').css({'border-color': 'rgb(224,224,224)'});
            }else{
                $('.start-date input, .end-date input').css({'border-style':'solid', 'border-width': '1px',
                    'border-color': 'rgb(255, 0, 0)'});
            }
        },
    });
    gui.define_popup({name:'cash_inout_statement_popup', widget: PrintCashInOutStatmentPopup});

    var AddMoneyToCreditPopup = PopupWidget.extend({
        template: 'AddMoneyToCreditPopup',
	    show: function(options){
	        var self = this;
	        this.client = options.new_client ? options.new_client : false;
	        var cust_due = this.pos.get_customer_due(this.client);
	        this.cust_due = cust_due.toFixed(2);
            this._super();
            $('#amount-to-be-added').focus();
	    },
	    click_confirm: function(){
            var self = this;
            var order = this.pos.get_order();
            if($('#amount-to-be-added').val() == ""){
                alert(_t('Please, enter amount!'));
                return;
            }
            var get_journal_id = Number($('.select-journal').val());
            var amt_due = self.cust_due;
            var amount = Number($('#amount-to-be-added').val());
            var pos_session_id = self.pos.pos_session.name;
            var partner_id = Number($('.client-line.highlight').attr('-id')) || Number($('.client-line.lowlight').attr('data-id'));
            var client = self.pos.get_order().get_client()
            partner_id = partner_id ? partner_id : client.id;
            var cashier_id = self.pos.get_cashier().id;
            this.pay_due = $("#pay_amount").prop('checked');
            var params = {
                model: 'account.payment',
                method: "payment",
                args: [get_journal_id, amount, pos_session_id, partner_id, cashier_id, this.pay_due],
            }
            rpc.query(params, {async: false}).then(function(vals){
                if(vals){
                	if(vals.affected_order && vals.affected_order[0]){
                		if(self.pos.get('pos_order_list') && self.pos.get('pos_order_list').length > 0){
                			_.each(self.pos.get('pos_order_list'),function(order){
                				_.each(vals.affected_order,function(new_order){
                					if(order.id == new_order[0].id){
                						if(new_order[0].amount_total && new_order[0].amount_paid){
                							order.amount_due = new_order[0].amount_total - new_order[0].amount_paid;
            							}
                					}
                				});
                			});
                		}
                	}
                	var partner = self.pos.db.get_partner_by_id(partner_id);
                	partner.remaining_credit_amount = vals.credit_bal;
                    self.gui.show_screen('receipt');
                    $('.pos-receipt-container', this.$el).html(QWeb.render('AddedCreditReceipt',{
                        widget: self,
                        order: order,
                        get_journal_id: get_journal_id,
                        amount: vals.credit_bal,
                        amt_due: vals.amount_due,
                        pay_due: self.pay_due,
                        partner_id: partner_id,
                    }));
                }
            });
        },
        renderElement: function() {
            var self = this;
	    	self._super();
            $('#pay_amount').click(function(){
                if (!$(this).is(':checked')) {
                    $("#amount-to-be-added").val("");
                }else{
                    $("#amount-to-be-added").val(self.cust_due)
                }
            })
        },
        export_as_JSON: function() {
            var pack_lot_ids = [];
            if (this.has_product_lot){
                this.pack_lot_lines.each(_.bind( function(item) {
                    return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
                }, this));
            }
            return {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
                tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
                id: this.id,
                pack_lot_ids: pack_lot_ids
            };
        },
    });
    gui.define_popup({name:'AddMoneyToCreditPopup', widget: AddMoneyToCreditPopup});


	var ProductPopup = PopupWidget.extend({
	    template: 'ProductPopup',
	    show: function(options){
	    	var self = this;
			this._super();
			this.order_lines = options.order_lines || false;
			this.order_id = options.order_id || false;
			this.state = options.state || false;
			this.order_screen_obj = options.order_screen_obj || false;
			this.renderElement();
            var order = self.pos.get_order();
	    },
	    click_confirm: function(){
	        if (this.state == "paid" || this.state == "done"){
	        	$("#re_order_duplicate[data-id='"+ this.order_id +"']").click();
	        } else if(this.state == "draft") {
	        	$("#edit_order[data-id='"+ this.order_id +"']").click();
			}
			this.gui.close_popup();
	    },
    	click_cancel: function(){
    		this.gui.close_popup();
    	}
	    
	});
	gui.define_popup({name:'product_popup', widget: ProductPopup});

});