// pos_orders_reprint js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_orders_reprint.pos_orders_reprint', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var SeeAllOrdersScreenWidget = require('pos_orders_list.pos_orders_list').SeeAllOrdersScreenWidget

    var _t = core._t;

    var SeeFormSendMailInvoice = popups.extend({
        template: "SeeFormSendMailInvoice",
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        events: {
            'click .button.cancel': 'click_cancel',
            'click .button.send_mail': 'send_mail',
        },
        show: function(options) {
            var self = this;
            options = options || {};
            this._super(options);
            this.order_id = options.order_id
        },
        send_mail: function() {
            var email = this.$("#email").val()
            var self = this;
            rpc.query({
                model: 'pos.order',
                method: 'send_mail',
                args: [
                    [this.order_id], email
                ]
            }).then(function(output) {
                console.log("El correo se envió correctamente")
                self.gui.close_popup();
                window.alert("El correo se envió correctamente")
            });

        }
    })

    gui.define_popup({
        name: 'see_form_send_mail_invoice',
        widget: SeeFormSendMailInvoice
    });

    var ReceiptScreenWidgetNew = screens.ScreenWidget.extend({
        template: 'ReceiptScreenWidgetNew',
        show: function() {
            var self = this;
            self._super();
            $('.button.back').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() {
                    self.chrome.screens.receipt.lock_screen(false);
                }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({
        name: 'ReceiptScreenWidgetNew',
        widget: ReceiptScreenWidgetNew
    });

    // pos_orders_list start
    SeeAllOrdersScreenWidget = SeeAllOrdersScreenWidget.extend({
        get_receipt_render_env_reprint:function(receipt){
            var self = this;
            var orderlines = receipt["orderlines"];
            var paymentlines = receipt["paymentlines"];
            var discount = receipt["discount"];
            var subtotal = receipt["subtotal"];
            var tax = receipt["tax"];
            var cliente = receipt["cliente"];
            var comprobante = receipt["comprobante"];
            var fecha_emision = receipt["fecha_emision"];
            var monto_letras = receipt["monto_letras"];
            var texto_qr = receipt["texto_qr"];
            var footer = receipt["footer"];
            var gravado = receipt["gravado"];
            var inafecto = receipt["inafecto"];
            var exonerado = receipt["exonerado"];
            var gratuito = receipt["gratuito"];
            var taxes = receipt["taxes"];
            var change = receipt["change"]

            return {
                widget: self,
                paymentlines: paymentlines,
                orderlines: orderlines,
                discount_total: discount,
                change: change,
                subtotal: subtotal,
                tax: tax,
                cliente: cliente,
                comprobante: comprobante,
                fecha_emision: fecha_emision,
                monto_letras: monto_letras,
                texto_qr: texto_qr,
                footer: footer,
                gravado:gravado,
                exonerado:exonerado,
                inafecto:inafecto,
                gratuito:gratuito,
                taxes:taxes,
                qr:texto_qr
            }
            
        },
        show: function(options) {
            var self = this;
            this._super(options);

            this.details_visible = false;

            var orders = self.pos.db.all_orders_list;
            //console.log("***************************************ordersssssssssssssss",orders)
            this.render_list_orders(orders, undefined);

            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });

            this.$('.orders-list-contents').delegate('.send-email-order', 'click', function(result) {
                var order_id = parseInt(this.id);
                self.gui.show_popup('see_form_send_mail_invoice', { "order_id": order_id });
            })

            this.$('.orders-list-contents').delegate('.print-order', 'click', function(result) {
                var order_id = parseInt(this.id);
                rpc.query({
                    model: 'pos.order',
                    method: 'print_pos_receipt',
                    args: [order_id],
                }).then(function(res) {
                    self.gui.show_screen('ReceiptScreenWidgetNew');
                    $('.pos-receipt-container2').html(QWeb.render('PosTicket1', self.get_receipt_render_env_reprint(res)));
                    jQuery('#qrcode2').qrcode({
                        width: 80,
                        height: 80,
                        text: res["texto_qr"]
                    });
                    
                });

            });
        },
    });

    gui.define_screen({
        name: 'see_all_orders_screen_widget',
        widget: SeeAllOrdersScreenWidget
    });

    return {
        SeeAllOrdersScreenWidget:SeeAllOrdersScreenWidget
    };
});