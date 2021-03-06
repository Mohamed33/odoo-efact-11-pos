/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_sync.pos_order_sync', function(require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var screens = require('point_of_sale.screens');
    var chrome = require('point_of_sale.chrome');
    var popup_widget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var pos_model = require('point_of_sale.models');
    var SuperGui = gui.Gui.prototype;
    var SuperOrder = pos_model.Order;
    var model_list = pos_model.PosModel.prototype.models;
    var SuperPosModel = pos_model.PosModel.prototype;
    var session_model = null;
    var core = require('web.core');
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var field_utils = require('web.field_utils');
    var round_di = utils.round_decimals;
    for (var i = 0, len = model_list.length; i < len; i++) {
        if (model_list[i].model == 'pos.session') {
            session_model = model_list[i];
            break;
        }
    }

    session_model.domain = function(self) {
            return [
                ['state', '=', 'opened']
            ];
        },

        session_model.loaded = function(self, pos_sessions) {
            var other_active_session = [];
            for (var i = 0, len = pos_sessions.length; i < len; i++) {
                if (pos_sessions[i].user_id[0] == self.user.id) {
                    self.pos_session = pos_sessions[i];
                } else
                    other_active_session.push(pos_sessions[i])
            }
            self.other_active_session = other_active_session;
            self.all_quotes = []
        }



    screens.OrderWidget = screens.OrderWidget.extend({
        bind_order_events: function() {
            var order = this.pos.get_order();
            //order.unbind('change:client', this.update_summary, this);
            //order.bind('change:client',   this.update_summary, this);
            order.unbind('change', this.update_summary, this);
            order.bind('change', this.update_summary, this);

            var lines = order.orderlines;
            lines.unbind('add', this.orderline_add, this);
            lines.bind('add', this.orderline_add, this);
            lines.unbind('remove', this.orderline_remove, this);
            lines.bind('remove', this.orderline_remove, this);
            lines.unbind('change', this.orderline_change, this);
            lines.bind('change', this.orderline_change, this);

        }
    })

    var orderline_id = 1;
    pos_model.Orderline = pos_model.Orderline.extend({
        init_from_JSON: function(json) {
            this.product = this.pos.db.get_product_by_id(json.product_id);
            if (!this.product) {
                console.error('ERROR: attempting to recover product ID', json.product_id,
                    'not available in the point of sale. Correct the product or clean the browser cache.');
            }
            this.set_product_lot(this.product);
            this.price = json.price_unit;
            this.set_discount(json.discount);
            this.set_quantity(json.qty, true);
            this.id = json.id;
            orderline_id = Math.max(this.id + 1, orderline_id);
            var pack_lot_lines = json.pack_lot_ids;
            for (var i = 0; i < pack_lot_lines.length; i++) {
                var packlotline = pack_lot_lines[i][2];
                var pack_lot_line = new exports.Packlotline({}, { 'json': _.extend(packlotline, { 'order_line': this }) });
                this.pack_lot_lines.add(pack_lot_line);
            }
        },
        export_as_JSON: function() {
            var pack_lot_ids = [];
            if (this.has_product_lot) {
                this.pack_lot_lines.each(_.bind(function(item) {
                    return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
                }, this));
            }
            return {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
                tax_ids: [
                    [6, false, _.map(this.get_applicable_taxes(), function(tax) { return tax.id; })]
                ],
                id: this.id,
                pack_lot_ids: pack_lot_ids
            };
        },
        set_quantity: function(quantity, keep_price) {
            this.order.assert_editable();
            if (quantity === 'remove') {
                this.order.remove_orderline(this);
                return;
            } else {
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();
                if (unit) {
                    if (unit.rounding) {
                        this.quantity = round_pr(quant, unit.rounding);
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        this.quantityStr = field_utils.format.float(round_di(this.quantity, decimals), { digits: [69, decimals] });
                    } else {
                        this.quantity = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                } else {
                    this.quantity = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }

            // just like in sale.order changing the quantity will recompute the unit price

            if (!keep_price) {
                //this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                console.log(this.get_unit_price())
                this.set_unit_price(this.price);
                console.log(this.get_unit_price())
                this.order.fix_tax_included_price(this);
            }
        }
    })


    pos_model.Order = pos_model.Order.extend({
        initialize: function(attributes, options) {
            var self = this;
            self.quote_id = null;
            self.quote_name = '';
            self.created_quote_id = null;
            SuperOrder.prototype.initialize.call(this, attributes, options);
        },
        export_as_JSON: function() {
            var self = this;
            var loaded = SuperOrder.prototype.export_as_JSON.call(this);
            if (self.quote_id != null)
                loaded.quote_id = self.quote_id;
            return loaded;
        },
        set_pricelist: function(pricelist) {
            var self = this;
            this.pricelist = pricelist;
            _.each(this.get_orderlines(), function(line) {
                //line.set_unit_price(line.product.get_price(self.pricelist, line.get_quantity()));
                line.set_unit_price(line.price);
                self.fix_tax_included_price(line);
            });
            this.trigger('change');
        },
    });

    pos_model.PosModel = pos_model.PosModel.extend({
        _save_to_server: function(orders, options) {
            var self = this;
            return SuperPosModel._save_to_server.call(this, orders, options).then(function(return_dict) {
                _.each(orders, function(order) {
                    //------------Code  for POS MULtI SESSION --start-------------------
                    $('#quote_history').css('color', 'rgb(94, 185, 55)');
                    if (order.data.quote_id) {
                        rpc.query({
                            model: 'pos.quote',
                            method: 'change_state_done',
                            args: [{ "quote_id": order.data.quote_id }],
                        })
                    }
                    self.db.remove_order(order.id);
                });
                var quote_list = [];
                var result_list_length;
                var all_quotes = self.all_quotes;
                var session_id = self.pos_session.id
                all_quotes.forEach(function(quote) {
                    quote_list.push(quote.quote_id);
                });
                var current_session = self.pos_session
                rpc.query({
                        model: 'pos.quote',
                        method: 'search_all_record',
                        args: [{
                            "quote_ids": quote_list,
                            "session_id": session_id
                        }],
                    })
                    .done(function(result) {
                        result_list_length = result.quote_list
                        if (result_list_length.length) {
                            result.quote_list.forEach(function(quote) {
                                all_quotes.unshift(quote);
                            });
                        }
                        self.all_quotes = all_quotes;
                        if (self.all_quotes.length)
                            $('#new_quote_notification').css('color', 'rgb(79, 207, 228)');
                        else
                            $('#new_quote_notification').css('color', 'rgb(58, 133, 141)');
                        $('.quotation_count').text(self.all_quotes.length);
                    });

                //Code  for POS MULtI SESSION --end- 
                self.set('failed', false);
                return return_dict;
            });
        }
    });

    screens.ReceiptScreenWidget.include({
        show: function() {
            var self = this;
            self._super();
            var all_quotes = self.pos.all_quotes;
            var index = null;
            var current_order = self.pos.get_order();
            if (current_order.quote_name) {
                for (var i = 0; i < all_quotes.length; i++) {
                    if (all_quotes[i].quote_id == current_order.quote_name) {
                        index = i;
                        break;
                    }
                }
            }
            if (index != null)
                all_quotes.splice(index, 1);
            self.pos.all_quotes = all_quotes;
            if (all_quotes.length == 0)
                $('#new_quote_notification').css('color', 'rgb(58, 133, 141)');
        }
    });

    gui.Gui = gui.Gui.extend({
        show_screen: function(screen_name, params, refresh, skip_close_popup) {
            var self = this;
            SuperGui.show_screen.call(self, screen_name, params, refresh, skip_close_popup);
            if (screen_name && jQuery.inArray(screen_name, ['payment', 'products', 'clientlist']) >= 0) {
                $('#save_order_quote').show();
                $('#new_quote_notification').show();
            } else {
                $('#save_order_quote').hide();
                $('#new_quote_notification').hide();
            }
        }
    });

    chrome.SynchNotificationWidget.include({
        start: function() {
            var self = this;
            self._super();
            $('#new_quote_notification').css('color', 'rgb(58, 133, 141)');
            $('#save_order_quote').on('click', function() {
                var current_order = self.pos.get_order();
                if (current_order.orderlines.length == 0)
                    self.gui.show_popup('wk_error_notify', {
                        title: _t("Empty order!!!"),
                        body: _t("You can't send an empty order, Please add some product(s) in cart.")
                    });
                else {
                    rpc.query({
                            model: 'ir.sequence',
                            method: 'next_by_code',
                            args: ['pos.quote'],
                        })
                        .fail(function(unused, event) {
                            self.gui.show_popup('wk_error_notify', {
                                title: _t('Failed To Send Quotation'),
                                body: _t('Please make sure you are connected to the network.'),
                            });
                        })
                        .done(function(quote_sequence_id) {
                            self.gui.show_popup('save_as_order_quote', {});
                            $('#quote_note').focus();
                            $('#quote_id').text(quote_sequence_id);
                        });
                }
            });
            $('#new_quote_notification').on('click', function() {
                self.update_new_quote_list();
                setTimeout(function() {
                    $('.quotation_count').show();
                    $('.fa-shopping-cart').show();
                    $('.wk_loading').hide()
                    var all_quotes_length = self.pos.all_quotes.length;
                    if (all_quotes_length == 0) {
                        $("#order_quote_notification").text("No quote available");
                        $("#order_quote_notification").fadeIn();
                        setTimeout(function() {
                            $("#order_quote_notification").fadeOut();
                        }, 2000);

                    } else if (all_quotes_length == 1) {
                        var quote_dict = self.pos.all_quotes[0];
                        self.chrome.widget.order_selector.neworder_click_handler();
                        var new_order = self.pos.get_order();
                        new_order.set_client(self.pos.db.get_partner_by_id(quote_dict.partner_id[0]));
                        quote_dict.line.forEach(function(line) {
                            var orderline = new pos_model.Orderline({}, {
                                pos: self.pos,
                                order: new_order,
                                product: self.pos.db.get_product_by_id(line.product_id),
                            });
                            orderline.set_unit_price(line.price_unit);
                            orderline.set_discount(line.discount);
                            orderline.set_quantity(line.qty);
                            new_order.add_orderline(orderline);
                        });
                        new_order.quote_id = quote_dict.quote_obj_id;
                        new_order.quote_name = quote_dict.quote_id;
                    } else {
                        self.gui.show_screen('wk_all_quote');
                    }
                }, 1500);
            });
            $("#quote_history").on('click', function() {
                rpc.query({
                        model: 'pos.quote',
                        method: 'load_quote_history',
                        args: [{
                            'session_id': self.pos.pos_session.id
                        }],
                    })
                    .done(function(result) {
                        self.pos.history = result.quote_list
                        $('#quote_history').css('color', 'rgb(94, 185, 55)');
                        self.gui.show_popup('wk_load_history', {
                            qoutes: self.pos.history
                        });
                    })
                    .fail(function(unused, event) {
                        $("#quote_history").css('color', 'red');
                        self.gui.show_popup('wk_error_notify', {
                            title: _t('Failed to show quotation history'),
                            body: _t('Please make sure you are connected to the network.'),
                        });
                    });
            });
        },
        update_new_quote_list: function() {
            var self = this;
            var session_id = self.pos.pos_session.id
            var quote_list = [];
            self.pos.all_quotes.forEach(function(quote) {
                quote_list.push(quote.quote_id);
            });
            var current_session = self.pos_session
            $('.quotation_count').hide();
            $('.fa-shopping-cart').hide();
            $('.wk_loading').show()
            rpc.query({
                    model: 'pos.quote',
                    method: 'search_all_record',
                    args: [{
                        "quote_ids": quote_list,
                        "session_id": session_id
                    }],
                })
                .done(function(result) {
                    result.quote_list.forEach(function(quote) {
                        self.pos.all_quotes.unshift(quote);
                    });
                    if (self.pos.all_quotes.length)
                        $('#new_quote_notification').css('color', 'rgb(79, 207, 228)');
                    else
                        $('#new_quote_notification').css('color', 'rgb(58, 133, 141)');
                    $('.quotation_count').text(self.pos.all_quotes.length)
                });
            $('.quotation_count').text(self.pos.all_quotes.length)
        }
    });
    var QuoteHistoryPopupWidget = popup_widget.extend({
        template: 'QuoteHistoryPopupWidget',
        events: {
            'click .button.cancel': 'click_cancel'
        },
    });
    gui.define_popup({ name: 'wk_load_history', widget: QuoteHistoryPopupWidget });

    var QuoteSendPopopWidget = popup_widget.extend({
        template: 'QuoteSendPopopWidget',
        events: {
            'click .button.cancel': 'click_cancel'
        },
        show: function(options) {
            var self = this;
            self._super(options)
            this.options = options;
            this.$('.order_status').show();
            $('#order_sent_status').hide();
            this.$('.order_status').removeClass('order_done');
            this.$('.show_tick').hide();
            setTimeout(function() {
                $('.order_status').addClass('order_done');
                $('.show_tick').show();
                $('#order_sent_status').show();
                $('.order_status').css({ 'border-color': '#5cb85c' })
            }, 500)
            if (!(self.options && self.options.quote_status)) {
                setTimeout(function() {
                    self.pos.get_order().destroy({
                        'reason': 'abandon'
                    });
                }, 1500)
            } else {
                setTimeout(function() {
                    self.click_cancel();
                }, 1500)
            }
        },

        click_cancel: function() {
            this.pos.gui.close_popup();
        }
    });
    gui.define_popup({
        name: 'quote_send',
        widget: QuoteSendPopopWidget
    });

    var WkErrorNotifyPopopWidget = popup_widget.extend({
        template: 'WkErrorNotifyPopopWidget',
        events: {
            'click .button.cancel': 'click_cancel'
        },
        show: function(options) {
            var self = this;
            self._super(options);
            this.options = options;

        }
    });
    gui.define_popup({
        name: 'wk_error_notify',
        widget: WkErrorNotifyPopopWidget
    });

    var AllQuotesListScreenWidget = screens.ScreenWidget.extend({
        template: 'AllQuotesListScreenWidget',
        show_leftpane: false,
        previous_screen: 'products',

        init: function(parent, options) {
            this._super(parent, options);
        },

        render_list: function(quote_list, input_txt) {
            var new_order_data = [];
            var self = this;
            if (input_txt != undefined && input_txt != '') {
                var search_text = input_txt.toLowerCase()
                for (i = 0; i < quote_list.length; i++) {
                    if (quote_list[i].partner_id[1] == false) {
                        quote_list[i].partner_id = [0, '-'];
                    }
                    if (((quote_list[i].quote_id.toLowerCase()).indexOf(search_text) != -1) ||
                        ((quote_list[i].from_session_id.toLowerCase()).indexOf(search_text) != -1) ||
                        ((quote_list[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                        new_order_data = new_order_data.concat(quote_list[i]);
                    }
                }
                quote_list = new_order_data;
            }
            var contents = this.$el[0].querySelector('.wk-quote-list-contents');
            contents.innerHTML = "";
            quote_list.forEach(function(order) {
                var orderline_html = QWeb.render('WkQuoteLine', {
                    widget: self,
                    order: order
                });
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            });
        },

        show: function() {
            var self = this;
            this._super();
            var quotes = self.pos.all_quotes;
            self.render_list(quotes);
            this.$('.order_search').keyup(function() {
                self.render_list(quotes, this.value);
            });

            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
            this.$('.wk-qoute-line .cancelar').on('click', function(event) {
                var clicked_quote_id = this.id

                rpc.query({
                        model: "pos.quote",
                        method: "cancelar_orden",
                        args: [{ "quote_id": clicked_quote_id }]
                    })
                    .done(function(result) {
                        self.$('.wk-qoute-line #' + clicked_quote_id).remove()
                        self.pos.all_quotes = self.pos.all_quotes.filter(function(quote) {
                            if (quote.quote_id == clicked_quote_id) {
                                return false
                            }
                            return true;
                        });
                    })
            })

            this.$('.wk-qoute-line .line').on('click', function(event) {
                var clicked_quote_id = this.id
                var quote_dict;
                quotes.forEach(function(quote) {
                    if (quote.quote_id == clicked_quote_id) {
                        quote_dict = quote;
                        console.log(quote)
                    }
                });

                self.gui.show_screen('products');
                self.chrome.widget.order_selector.neworder_click_handler();
                var new_order = self.pos.get_order();
                new_order.set_client(self.pos.db.get_partner_by_id(quote_dict.partner_id[0]));
                quote_dict.line.forEach(function(line) {
                    var orderline = new pos_model.Orderline({}, {
                        pos: self.pos,
                        order: new_order,
                        product: self.pos.db.get_product_by_id(line.product_id),
                    });
                    orderline.set_unit_price(line.price_unit, 'set line price unit');
                    orderline.set_discount(line.discount);
                    orderline.set_quantity(line.qty, 'set line price');
                    new_order.add_orderline(orderline);
                });
                new_order.quote_id = quote_dict.quote_obj_id;
                new_order.quote_name = quote_dict.quote_id;
                self.pos.gui.show_popup('quote_send', {
                    'quote_status': 'Order Loaded !!!'
                });
            });
        },
        close: function() {
            this._super();
            this.$('.wk-quote-list-contents').undelegate();
        },
    });
    gui.define_screen({ name: 'wk_all_quote', widget: AllQuotesListScreenWidget });

    var SaveAsOrderQuotePopupWidget = popup_widget.extend({
        template: 'SaveAsOrderQuotePopupWidget',
        events: {
            'click .button.cancel': 'click_cancel',
            'click .button.confirm': 'click_confirm',
            'click .selection-item': 'click_item',
            'click .input-button': 'click_numpad',
            'click .mode-button': 'click_numpad',
            'click #wk_save_order_quote': 'click_wk_save_order_quote',
            'click #wk_print_and_save': 'click_wk_print_and_save',
            'focus #quote_note': 'focus_quote_note',
            'focusout #quote_note': 'focusout_quote_note',
        },
        init: function(parent, options) {
            this._super(parent, options);
            this.selected_session_id = null;
        },
        renderElement: function() {
            var self = this;
            self._super();
            this.selected_session_id = null;
            $('.select_session').on('click', function() {
                $("#order_quote_id_input_error").hide();
                $(".select_session").css('background', 'white')
                self.selected_session_id = parseInt($(this).attr('id'));
                $(this).css('background', '#6EC89B');
            });
        },
        focusout_quote_note: function() {
            var self = this;
            if (self.gui && self.gui.get_current_screen() == 'payment') {
                var paymentscreen = self.pos.gui.chrome.screens.payment

                $('body').keypress(paymentscreen.keyboard_handler);
                $('body').keydown(paymentscreen.keyboard_keydown_handler);
                window.document.body.addEventListener('keypress', paymentscreen.keyboard_handler);
                window.document.body.addEventListener('keydown', paymentscreen.keyboard_keydown_handler);
            }
        },
        focus_quote_note: function() {
            var self = this;
            if (self.gui && self.gui.get_current_screen() == 'payment') {
                var paymentscreen = self.pos.gui.chrome.screens.payment
                $('body').off('keypress', paymentscreen.keyboard_handler);
                $('body').off('keydown', paymentscreen.keyboard_keydown_handler);
                window.document.body.removeEventListener('keypress', paymentscreen.keyboard_handler);
                window.document.body.removeEventListener('keydown', paymentscreen.keyboard_keydown_handler);
            }
        },
        click_wk_save_order_quote: function(print_order_quote) {
            var self = this;
            var current_order = self.pos.get_order();
            var order_vals = {};
            var session_id = self.selected_session_id;
            if (!(session_id)) {
                $(".select_session").css("background-color", "burlywood");
                setTimeout(function() {
                    $(".select_session").css("background-color", "");
                }, 100);
                setTimeout(function() {
                    $(".select_session").css("background-color", "burlywood");
                }, 200);
                setTimeout(function() {
                    $(".select_session").css("background-color", "");
                }, 300);
                setTimeout(function() {
                    $(".select_session").css("background-color", "burlywood");
                }, 400);
                setTimeout(function() {
                    $(".select_session").css("background-color", "");
                }, 500);
                return;
            } else {
                order_vals.to_session_id = session_id;
                self.to_session_id = session_id;
                order_vals.date_order = current_order.creation_date;
                order_vals.user_id = self.pos.cashier ? self.pos.cashier.id : self.pos.user.id;
                if (current_order.get_client()) {
                    order_vals.partner_id = current_order.get_client().id
                }
                order_vals.session_id = self.pos.pos_session.id;
                order_vals.pricelist_id = current_order.pricelist.id;
                order_vals.note = self.$("#quote_note").val();
                order_vals.quote_id = self.$("#quote_id").text();
                order_vals.amount_total = current_order.get_total_with_tax();
                order_vals.amount_tax = current_order.get_total_tax();
                order_vals.amount_paid = current_order.get_total_paid();
                order_vals.amount_return = current_order.get_change();
                if (self.$("#quote_id").text() == '') {
                    self.$('#order_quote_id_input_error').text("No Quote Id Found.");
                    self.$('#order_quote_id_input_error').css("width", "66%");
                    self.$('#order_quote_id_input_error').css("padding-left", "26%");
                    self.$('#order_quote_id_input_error').show();
                } else {
                    rpc.query({
                            model: 'pos.quote',
                            method: 'search_quote',
                            args: [{ 'quotation_id': self.$("#quote_id").text() }],
                        })
                        .fail(function(unused, event) {
                            self.gui.show_popup('wk_error_notify', {
                                title: _t('Failed To Save Quotation.'),
                                body: _t('Please make sure you are connected to the network.'),
                            });
                        })
                        .done(function(result) {

                            if (result != null) {
                                self.$('#order_quote_id_input_error').text("This Quote Id has Already been used.");
                                self.$('#order_quote_id_input_error').css("width", "75%");
                                self.$('#order_quote_id_input_error').css("padding-left", "18%");
                                self.$('#order_quote_id_input_error').show();
                            } else {
                                rpc.query({
                                        model: 'pos.quote',
                                        method: 'create',
                                        args: [order_vals],
                                    })
                                    .fail(function(unused, event) {
                                        self.gui.show_popup('wk_error_notify', {
                                            title: _t('Failed To Save Quotation'),
                                            body: _t('Please make sure you are connected to the network.'),
                                        });
                                    })
                                    .done(function(new_quote_id) {
                                        if (print_order_quote)
                                            self.pos.get_order().created_quote_id = new_quote_id;
                                        
                                        var orderlines = self.pos.get_order().get_orderlines();
                                        orderlines.forEach(function(orderline,index) {
                                            var order_line_vals = {};
                                            order_line_vals.sequence = index+1;
                                            order_line_vals.quote_id = new_quote_id;
                                            order_line_vals.product_id = orderline.product.id;
                                            order_line_vals.price_unit = orderline.get_unit_display_price();
                                            order_line_vals.qty = orderline.quantity;
                                            order_line_vals.discount = orderline.discount;
                                            order_line_vals.price_subtotal = orderline.get_price_without_tax();
                                            order_line_vals.price_subtotal_incl = orderline.get_price_with_tax();
                                            var tax_ids = [];
                                            orderline.product.taxes_id.forEach(function(tax_id) {
                                                tax_ids.push(tax_id);
                                            });
                                            order_line_vals.quote_tax_ids = tax_ids;
                                            rpc.query({
                                                    model: 'pos.quote.line',
                                                    method: 'create',
                                                    args: [order_line_vals],
                                                })
                                                .fail(function(unused, event) {
                                                    self.gui.show_popup('wk_error_notify', {
                                                        title: _t('Failed To Save Quotation'),
                                                        body: _t('Please make sure you are connected to the network.'),
                                                    });
                                                })
                                        });
                                        self.pos.gui.show_popup('quote_send');
                                    });
                            }
                        });
                }
            }
        },
        click_wk_print_and_save: function() {
            var self = this;
            self.click_wk_save_order_quote(true);
            if (self.selected_session_id) {
                if (self.pos.config.quotation_print_type == 'pdf') {
                    setTimeout(function() {
                        self.chrome.do_action('pos_order_sync.report_quote', {
                            additional_context: {
                                active_ids: [self.pos.get_order().created_quote_id],
                            }
                        });
                    }, 1000)
                } else if (self.pos.config.quotation_print_type == 'posbox') {
                    var order = self.pos.get_order();
                    var to_session = _.filter(self.pos.other_active_session, function(session) {
                        return (session.id == self.to_session_id)
                    });
                    var quote = {
                        'quote_id': self.$("#quote_id").text(),
                        'from_session': self.pos.pos_session.config_id[1],
                    }
                    if (to_session)
                        quote['to_session'] = to_session[0].config_id[1];
                    var result = {
                        widget: self,
                        pos: self.pos,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order.get_orderlines(),
                        quote: quote,
                    }
                    var receipt = QWeb.render('OrderSyncXmlReceipt', result);
                    self.pos.proxy.print_receipt(receipt);
                }
            }
        },
    });
    gui.define_popup({ name: 'save_as_order_quote', widget: SaveAsOrderQuotePopupWidget });
});