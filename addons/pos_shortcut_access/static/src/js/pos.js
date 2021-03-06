odoo.define('pos_shortcut_access.pos_shortcut_access', function(require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require("point_of_sale.popups");
    var models = require('point_of_sale.models');
    var _t = core._t;
    models.load_fields("account.bank.statement", ['payment_meth_sc']);
    chrome.Chrome.include({
        build_widgets: function() {
            var self = this;
            var config = self.pos.config;
            $.key(config.qty_select_sc, function(event) {
                $(".mode-button[data-mode='quantity']").click();
            });
            $.key(config.dis_select_sc, function(event) {
                $(".mode-button[data-mode='discount']").click();
            });
            $.key(config.price_select_sc, function(event) {
                $(".mode-button[data-mode='price']").click();
            });
            $.key(config.payment_sc, function() {
                $(".pay").click();
            });
            $.key(config.change_user_sc, function() {
                $(".username").click();
            });
            $.key(config.change_customer_sc, function() {
                $(".set-customer").click();
            });
            $.key(config.select_search_box_sc, function() {
                $(".searchbox input").select();
            });
            $.key(config.add_new_order_sc, function() {
                $(".neworder-button").click();
            });
            $.key(config.remove_order_sc, function() {
                $(".deleteorder-button").click();
            });
            $.key(config.back_button_sc, function() {
                $(".back").click();
            });
            $.key(config.cancel_button_sc, function() {
                $(".cancel").click();
            });
            $.key(config.next_order_sc, function() {
                $(".next").click();
            });
            // $.key(config.next_order_sc,function(){
            // 	$(".next").click();
            // });
            $.key(config.remove_order_line_sc, function() {
                if (self.gui.get_current_screen() == 'products' && !$(".searchbox input").is(":focus")) {
                    $(".subwindow-container-fix .numpad-backspace").click();
                }
            });
            $("body").keypress(function(event) {
                console.log(event.which)
                if (self.gui.get_current_screen() == 'products') {
                    if (!$(".searchbox input").is(":focus")) {

                        if (event.which == 49) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('1')").click();
                        } else if (event.which == 50) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('2')").click();
                        } else if (event.which == 51) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('3')").click();
                        } else if (event.which == 52) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('4')").click();
                        } else if (event.which == 53) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('5')").click();
                        } else if (event.which == 54) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('6')").click();
                        } else if (event.which == 55) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('7')").click();
                        } else if (event.which == 56) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('8')").click();
                        } else if (event.which == 57) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('9')").click();
                        } else if (event.which == 48) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('0')").click();
                        } else if (event.which == 46) {
                            $(".leftpane .subwindow-container-fix .number-char:contains('.')").click();
                        } else if (event.which == 127) {
                            console.log(127)
                            $(".leftpane .subwindow-container-fix .input-button .numpad-backspace").click();
                        }

                    }
                    if ($(".searchbox input").is(":focus")) {
                        if (event.which == 13) {
                            setTimeout(function() { $(".searchbox input").blur(); }, 100);

                        }
                    }
                }
            });
            var cashregisters = self.pos.cashregisters;
            _.each(cashregisters, function(statement) {
                $.key(statement.payment_meth_sc, function(event) {
                    if (self.gui.get_current_screen() == 'payment') {
                        $(".paymentmethod[data-shortcut='" + statement.payment_meth_sc + "']").click();
                        event.preventDefault();
                        event.stopPropagation();
                    }
                });
            });

            this._super();
        },
    });
});