odoo.define('aspl_pos.screens', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    //var Model = require('web.DataModel');
    var rpc = require('web.rpc');
    var models = require('point_of_sale.models');

    var _t = core._t;
    var QWeb = core.qweb;

    var ShowOrderList = screens.ActionButtonWidget.extend({
        template: 'ShowOrderList',
        button_click: function() {
            self = this;
            self.gui.show_screen('orderlist');
        },
    });

    screens.define_action_button({
        'name': 'showorderlist',
        'widget': ShowOrderList,
    });

    screens.ReceiptScreenWidget.include({
        show: function() {
            this._super();
            var self = this;

            var barcode_val = this.pos.get_order().get_name();
            if (barcode_val.indexOf(_t("Order ")) != -1) {
                var vals = barcode_val.split(_t("Order "));
                if (vals) {
                    var barcode = vals[1];
                    $("tr#barcode1").html($("<td style='padding:2px 2px 2px 0px; text-align:center;'><div class='" + barcode + "' width='150' height='50'/></td>"));
                    $("." + barcode.toString()).barcode(barcode.toString(), "code128");
                }
            }
        },
    });


    var ReturnPaymentScreenWidget = screens.PaymentScreenWidget.prototype;
    screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            var order = self.pos.get_order();
            if (order) {
                var currentOrderLines = order.get_orderlines();
                this.$('#btn_so').click(function() {
                    if (!order.is_paid()) {
                        return
                    }
                    var paymentline_ids = [];
                    if (order.get_paymentlines().length > 0) {
                        if (currentOrderLines.length <= 0) {
                            alert('Empty order');
                        } else if (order.get_client() == null) {
                            alert('Customer is not selected !');
                        } else {
                            var customer_id = order.get_client().id;
                            var orderLines = [];
                            for (var i = 0; i < currentOrderLines.length; i++) {
                                orderLines.push(currentOrderLines[i].export_as_JSON());
                            }
                            var paymentlines = [];
                            _.each(order.get_paymentlines(), function(paymentline) {
                                paymentlines.push({
                                    'journal_id': paymentline.cashregister.journal_id[0],
                                    'amount': paymentline.get_amount(),
                                })
                            })
                            $('#btn_so').hide();
                            var location_id = self.pos.config.stock_location_id ? self.pos.config.stock_location_id[0] : false
                                /*
                                new Model('sale.order').call('create_sales_order', [orderLines, customer_id, self.pos.pos_session.id, location_id, paymentlines, self.pos.config.so_sequence,
                                    { 'paid': true, 'from_pos': true }
                                ])*/
                            rpc.query({
                                    model: 'sale.order',
                                    method: 'create_sales_order',
                                    args: [orderLines, customer_id, self.pos.pos_session.id, location_id, paymentlines, self.pos.config.so_sequence,
                                        { 'paid': true, 'from_pos': true }
                                    ],
                                })
                                .then(function(sale_order) {
                                    $('#btn_so').show();
                                    if (sale_order) {
                                        order.set_sale_order_name(sale_order[1]);
                                    }
                                    self.gui.show_screen('receipt');
                                }, function(err, event) {
                                    $('#btn_so').show();
                                    event.preventDefault();
                                    self.gui.show_popup('error', {
                                        'title': _t('Error: Could not Save Changes'),
                                        'body': _t('Your Internet connection is probably down.'),
                                    });
                                });
                        }
                    }
                });
            }
        },
        wait: function(callback, seconds) {
            return window.setTimeout(callback, seconds * 1000);
        },
        order_changes: function() {
            var self = this;
            var order = this.pos.get_order();
            if (!order) {
                return;
            } else if (order.is_paid()) {
                self.$('.next').addClass('highlight');
                self.$('#btn_so').addClass('highlight');
            } else {
                self.$('.next').removeClass('highlight');
                self.$('#btn_so').removeClass('highlight');
            }
        },
        click_back: function() {
            var order = this.pos.get_order();
            if (order.get_return_order()) {
                this.gui.show_popup('confirm', {
                    title: _t('Discard Return Operation'),
                    body: _t('Press confirm button to discard return operation.'),
                    confirm: function() {
                        order.destroy();
                    },
                });
            } else {
                this._super();
            }
        },
    });

    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if (mode === 'quantity') {
                    if (order.get_selected_orderline().get_dont_remove()) {
                        return;
                    }
                    var line_qty = 0;
                    var currentOrderLines = order.get_orderlines();
                    _.each(currentOrderLines, function(item) {
                        if (!item.selected && item.get_serial() === order.get_selected_orderline().get_serial()) {
                            line_qty += item.get_quantity();
                        }
                    });
                    if (order.get_selected_orderline().get_serial() && ((val != 'remove' && val.length != 0)) && (val != 'remove')) {
                        if (order.get_selected_orderline().product.tracking == "lot") {
                            var act_qty = Number(val) + Number(line_qty);
                            if (order.get_selected_orderline().get_remainig_lot() < act_qty) {
                                alert('Not allow more than ' + order.get_selected_orderline().get_remainig_lot() + ' quantity');
                                return;
                            } else {
                                order.get_selected_orderline().set_quantity(val);
                            }
                        } else {
                            alert('Can not change quantity this is unique serial of item');
                            return;
                        }
                    } else {
                        order.get_selected_orderline().set_quantity(val);
                    }
                    if (val != 'remove' && val.length > 0) {
                        order.get_selected_orderline().set_input_lot_serial(order.get_selected_orderline().get_serial(), val);
                    }
                } else if (mode === 'discount') {
                    order.get_selected_orderline().set_discount(val);
                } else if (mode === 'price') {
                    order.get_selected_orderline().set_unit_price(val);
                }
            }
        },
    });

    var ConfirmButton = screens.ActionButtonWidget.extend({
        template: 'ConfirmButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var currentOrderLines = order.get_orderlines();
            if (currentOrderLines.length <= 0) {
                alert('No product selected !');
            } else if (order.get_client() == null) {
                alert('Customer is not selected !');
            } else {
                var customer_id = order.get_client().id;
                var orderLines = [];
                for (var i = 0; i < currentOrderLines.length; i++) {
                    orderLines.push(currentOrderLines[i].export_as_JSON());
                }
                /*
                new Model('sale.order').call('create_sales_order', [orderLines, customer_id, self.pos.pos_session.id, false, false, self.pos.config.so_sequence,
                        { 'confirm': true, 'from_pos': true }
                    ])
                    */
                rpc.query({
                    model: "sale.order",
                    method: "create_sales_order",
                    args: [orderLines, customer_id, self.pos.pos_session.id, false, false, self.pos.config.so_sequence,
                        { 'confirm': true, 'from_pos': true }
                    ]
                }).then(function(sale_order) {
                    if (sale_order) {
                        order.set_sale_order_name(sale_order[1]);
                        self.gui.show_screen('receipt');
                    }
                }, function(err, event) {
                    event.preventDefault();
                    self.gui.show_popup('error', {
                        'title': _t('Error: Could not Save Changes'),
                        'body': _t('Your Internet connection is probably down.'),
                    });
                });
            }
        },
    });

    screens.define_action_button({
        'name': 'ConfirmButton',
        'widget': ConfirmButton,
        'condition': function() {
            return this.pos.config.so_operation_confirm;
        },
    });

    var QuotationButton = screens.ActionButtonWidget.extend({
        template: 'QuotationButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var currentOrderLines = order.get_orderlines();
            if (currentOrderLines.length <= 0) {
                alert('No product selected !');
            } else if (order.get_client() == null) {
                alert('Customer is not selected !');
            } else {
                var customer_id = order.get_client().id;
                var orderLines = [];
                for (var i = 0; i < currentOrderLines.length; i++) {
                    orderLines.push(currentOrderLines[i].export_as_JSON());
                }
                //new Model('sale.order').call('create_sales_order', [orderLines, customer_id, self.pos.pos_session.id, false, false, self.pos.config.so_sequence, { 'from_pos': true }])
                rpc.query({
                    model: 'sale.order',
                    method: 'create_sales_order',
                    args: [orderLines, customer_id, self.pos.pos_session.id, false, false, self.pos.config.so_sequence, { 'from_pos': true }]
                }).then(function(sale_order) {
                    if (sale_order) {
                        order.set_sale_order_name(sale_order[1]);
                        self.gui.show_screen('receipt');
                    }
                }, function(err, event) {
                    event.preventDefault();
                    self.gui.show_popup('error', {
                        'title': _t('Error: Could not Save Changes'),
                        'body': _t('Your Internet connection is probably down.'),
                    });
                });
            }
        },
    });

    screens.define_action_button({
        'name': 'QuotationButton',
        'widget': QuotationButton,
        'condition': function() {
            return this.pos.config.so_operation_draft;
        },
    });

    /* ADD PRODUCT BUTTON */
    var AddProductButton = screens.ActionButtonWidget.extend({
        template: 'AddProductButton',
        button_click: function() {
            var self = this;
            self.gui.show_screen('productlist');
        },
    });

    screens.define_action_button({
        'name': 'add_product_button',
        'widget': AddProductButton,
        'condition': function() {
            return this.pos.config.enable_add_product;
        },
    });

    var ProductListScreenWidget = screens.ScreenWidget.extend({
        template: 'ProductListScreenWidget',

        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
        },
        start: function() {
            var self = this;
            this._super();
        },
        renderElement: function() {
            var self = this;
            self._super();
            var namelist = self.pos.db.get_products_name();
            $("#sale_price").keypress(function(e) {
                if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && e.which != 46) {
                    return false;
                }
            });
            //			$("#cost_price").keypress(function (e) {
            //                if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && e.which != 46) {
            //                	return false;
            //               }
            //            });
            $('input#search', this.el).keypress(function(e) {
                $('input#search', self.el).autocomplete({
                    source: namelist,
                });
                e.stopPropagation();
            });
        },
        show: function() {
            var self = this;
            this._super();
            this.renderElement();
            $('#search').focus();
            this.product_id = 0;
            var res = false;
            var new_options = [];
            var cat_options = [];
            var catg_id;
            $("#sale_price").keypress(function(e) {
                if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && e.which != 46) {
                    return false;
                }
            });
            new_options.push("<option value=''>Select Category</option>");
            var categories = self.pos.db.get_all_categories();
            _.each(categories, function(key, val) {
                new_options.push("<option value='" + categories[val].id + "'>" + categories[val].name + "</option>\n");
            });
            $('select.pos_category').html(new_options);

            var internal_cat = self.pos.product_category;
            _.each(internal_cat, function(key, val) {
                cat_options.push("<option value='" + internal_cat[val].id + "'>" + internal_cat[val].display_name + "</option>\n");
            });
            $('select.internal_category').html(cat_options);
            $('#search').keyup(function(e) {
                var keyword = $.trim($(this).val());
                if (keyword) {
                    if (e.which == 13) {
                        $('span.ui-helper-hidden-accessible').html("");
                        $('ul.ui-autocomplete').css('display', 'none');
                        if (res = self.pos.db.get_product_by_barcode(keyword)) {
                            self.product_id = res.product_tmpl_id;
                            self.prod_prod = res;
                        } else if (res = self.pos.db.get_product_by_reference(keyword)) {
                            self.product_id = res.product_tmpl_id;
                            self.prod_prod = res;
                        } else if (res = self.pos.db.get_product_by_name(keyword)) {
                            self.product_id = res.product_tmpl_id;
                            self.prod_prod = res;
                        } else {
                            self.product_id = 0;
                            self.prod_prod = false;
                        }
                        if (res) {
                            $('table.product-input-table input.name').val(res.display_name);
                            $('table.product-input-table input.sale_price').val(Number(res.list_price).toFixed(2));
                            $('table.product-input-table input.ean13').val(res.barcode != false ? res.barcode : "");
                            $('table.product-input-table input.internal_reference').val(res.default_code != false ? res.default_code : "");
                            $('table.product-input-table input.codigo_battery').val(res.codigo_battery != false ? res.codigo_battery : "");
                            $('table.product-input-table select.pos_category').val(res.pos_categ_id[0]);
                            $('table.product-input-table select.internal_category').val(res.categ_id[0]);
                            $('table.product-input-table select.product_type').val(res.type);
                        } else {
                            var domain = [
                                ['available_in_pos', '=', true], '|', '|', '|', ['barcode', '=', keyword],
                                ['barcode', '=', '0' + keyword],
                                ['default_code', '=', keyword],
                                ['name', '=', keyword]
                            ];
                            //new Model('product.template').get_func('search_read')(domain, ['display_name', 'list_price', 'barcode', 'default_code', 'standard_price', 'pos_categ_id', 'categ_id', 'codigo_battery'])
                            rpc.query({
                                model: "product.template",
                                method: "search_read",
                                args: [],
                                kwargs: {
                                    domain: domain,
                                    fields: ['display_name', 'list_price', 'barcode', 'default_code', 'standard_price', 'pos_categ_id', 'categ_id', 'codigo_battery']
                                }
                            }).then(function(product_res) {
                                if (product_res.length > 0) {
                                    res = product_res[0];
                                    $('table.product-input-table input.name').val(res.display_name);
                                    $('table.product-input-table input.sale_price').val(Number(res.list_price).toFixed(2));
                                    $('table.product-input-table input.ean13').val(res.barcode != false ? res.barcode : "");
                                    $('table.product-input-table input.internal_reference').val(res.default_code != false ? res.default_code : "");
                                    $('table.product-input-table input.codigo_battery').val(res.codigo_battery != false ? res.codigo_battery : "");
                                    $('table.product-input-table select.pos_category').val(res.pos_categ_id[0]);
                                    $('table.product-input-table select.internal_category').val(res.categ_id[0]);
                                    self.disable_form();
                                } else {
                                    $('#search').append('<audio src="/point_of_sale/static/src/sounds/error.wav" autoplay="true"></audio>');
                                    if (keyword != "") {
                                        alert("Product not found.")
                                        $('#search').focus();
                                        $('table.product-input-table input.name').val("");
                                        $('table.product-input-table input.sale_price').val("");
                                        $('table.product-input-table input.ean13').val("");
                                        $('table.product-input-table input.internal_reference').val("");
                                        $('table.product-input-table input.codigo_battery').val("");
                                        //                                            $('table.product-input-table input.cost_price').val('');
                                        $('table.product-input-table input.name').focus();
                                        $('#search').val("");
                                        self.enable_form();
                                    } else {
                                        alert("invalid search term");
                                    }
                                }
                            });
                        }
                        self.disable_form();
                        $(this).val("");
                    } else if (e.which == 8 || e.which == 46) {
                        if ($(this).val() == "") {
                            self.product_id = 0;
                            $('table.product-input-table input').val("");
                        }
                    }
                }
            });
            $('button.saveclose').click(function() {
                self._save_product(self.product_id);
            });
            $('button.clear').click(function() {
                var internal_cat = self.pos.product_category;
                var default_cat = internal_cat[0] ? internal_cat[0].id : $('select.internal_category').val();
                $('table.product-input-table input.name').val("");
                $('table.product-input-table input.sale_price').val("");
                $('table.product-input-table input.ean13').val("");
                $('table.product-input-table input.internal_reference').val("");
                $('table.product-input-table input.codigo_battery').val("");
                //				$('table.product-input-table input.cost_price').val("");
                $('table.product-input-table select.pos_category').val("");
                $('table.product-input-table select.internal_category').val(default_cat);
                $('table.product-input-table select.product_type').val('consu');
                self.product_id = 0;
                self.enable_form();
            });
            this.$('.back').click(function() {
                self.gui.back();
            });
        },
        disable_form: function() {
            $('table.product-input-table input.codigo_battery').val('');
            $('table.product-input-table input.codigo_battery').focus();;
            $('table.product-input-table input.name').prop('disabled', true);
            $('table.product-input-table input.sale_price').prop('disabled', true);
            $('table.product-input-table input.ean13').prop('disabled', true);
            $('table.product-input-table input.internal_reference').prop('disabled', true);
            $('table.product-input-table select.pos_category').prop('disabled', true);
            $('table.product-input-table select.internal_category').prop('disabled', true);
            $('table.product-input-table select.product_type').prop('disabled', true);
        },
        enable_form: function() {
            $('table.product-input-table input.name').prop('disabled', false);
            $('table.product-input-table input.sale_price').prop('disabled', false);
            $('table.product-input-table input.ean13').prop('disabled', false);
            $('table.product-input-table input.internal_reference').prop('disabled', false);
            $('table.product-input-table select.pos_category').prop('disabled', false);
            $('table.product-input-table select.internal_category').prop('disabled', false);
            $('table.product-input-table select.product_type').prop('disabled', false);
        },
        add_product_with_lot: function(product, sr_no, lot_id) {
            var temp = true;
            if (!product) {
                return $('button.clear').click();
            }
            var self = this;
            var order = self.pos.get_order();
            var line = new models.Orderline({}, { pos: self.pos, order: order, product: product });
            line.set_serial(sr_no);
            //            line.set_input_lot_serial(sr_no,1);
            line.set_serial_id(lot_id);
            line.set_dont_remove(true);

            line.set_operation_product(true);
            line.set_stock_income(true);
            if (this.$('.exchange_product').prop('checked')) {
                line.set_exchange_product(true)
            }
            var orderlines = order.get_orderlines();
            _.each(orderlines, function(item) {
                if (item.get_product().tracking == 'lot' && item.get_product().id == self.product_id && item.get_serial() == selected_serial_record.name) {
                    line_qty += item.get_quantity();
                }
                if (item.get_product().tracking != 'lot' && item.get_product().id == self.product_id && item.get_serial() == selected_serial_record.name) {
                    alert('Same product is already assigned with same serial number !');
                    sr_no = null;
                    temp = false;
                    return temp;
                }

            });
            if (temp) {
                order.set_from_product_operation(true);
                var last_orderline = order.get_last_orderline();
                if (last_orderline && last_orderline.can_be_merged_with(line)) {
                    last_orderline.merge(line);
                } else {
                    order.orderlines.add(line);
                }
                order.select_orderline(order.get_last_orderline());
                $('#btn_so').hide();
                self.gui.show_screen('products');
            }
        },
        _save_product: function(product_id) {
            var self = this;
            var internal_cat = self.pos.product_category;
            var default_cat = internal_cat[0] ? internal_cat[0].id : $('select.internal_category').val();
            var name = $('table.product-input-table input.name').val();
            var list_price = $('table.product-input-table input.sale_price').val();
            var ean13 = $('table.product-input-table input.ean13').val();
            var default_code = $('table.product-input-table input.internal_reference').val();
            var codigo_battery = $('table.product-input-table input.codigo_battery').val();
            var pos_categ_id = $('table.product-input-table select.pos_category').val();
            var categ_id = $('table.product-input-table select.internal_category').val();
            var product_type = $('table.product-input-table select.product_type').val();
            if (name != "" && name != undefined && name != null) {
                var vals = {
                    "name": name,
                    "list_price": list_price,
                    "barcode": ean13 === "" ? false : ean13,
                    "default_code": default_code,
                    "codigo_battery": codigo_battery,
                    "pos_categ_id": pos_categ_id,
                    "categ_id": categ_id,
                    "type": product_type,
                    "location_id": self.pos.config.stock_location_id ? self.pos.config.stock_location_id[0] : false,
                };
                if (self.product_id <= 0) {
                    var avail_barcode = self.pos.db.get_product_by_barcode(ean13);
                    if (!avail_barcode) {
                        //new Model("product.template").call("create", [vals])
                        rpc.query({
                            model: 'product.template',
                            method: 'create',
                            args: [vals]
                        }).then(function(res) {
                            if (res) {
                                /*
                                new Model('product.product').get_func('search_read')
                                    ([
                                        ['product_tmpl_id', '=', res]
                                    ], _.find(self.pos.models, function(model) { return model.model === 'product.product'; }).fields)
                                */
                                rpc.query({
                                    model: 'product.product',
                                    method: 'search_read',
                                    args: [],
                                    kwargs: {
                                        domain: [
                                            ['product_tmpl_id', '=', res]
                                        ],
                                        fields: (_.find(self.pos.models, function(model) { return model.model === 'product.product'; }).fields)
                                    }
                                }).then(function(product) {
                                    if (product.length > 0) {
                                        product_id = 0;
                                        product[0]["display_name"] = product[0]['name'];
                                        product[0]["price"] = product[0]['list_price'];
                                        $('table.product-input-table input').val("");
                                        $('select.internal_category').val(default_cat);
                                        $('select.pos_category').val("");
                                        $('select.product_type').val('consu');
                                        self.pos.db.add_products(product);
                                        vals['product_tmpl_id'] = res;
                                        /*
                                        new Model("product.template").call("add_lot_serials", [
                                            [], vals
                                        ])*/
                                        rpc.query({
                                            model: "product.template",
                                            method: "add_lot_serials",
                                            args: [
                                                [], vals
                                            ]
                                        }).then(function(lot_id) {
                                            if (lot_id) {
                                                self.add_product_with_lot(product[0], vals['codigo_battery'], lot_id);
                                            }
                                        }).fail(function(error, event) {
                                            event.preventDefault();
                                            self.gui.show_popup('error', {
                                                'title': _t("Error"),
                                                'body': _t("Product Sucessfully Added but" + error.data.message),
                                            });
                                        });
                                    }
                                });
                            }
                        }).fail(function(error, event) {
                            event.preventDefault();
                            self.gui.show_popup('error', {
                                'title': _t("Error"),
                                'body': _t(error.data.message),
                            });
                        });
                    } else {
                        alert("Product barcode already exist.");
                    }
                } else {
                    if (self.prod_prod.type == "service" && !vals['codigo_battery']) {
                        return
                    }
                    if (!confirm(_t("Are you sure you want to add this product Codigo Battery ?"))) {
                        return;
                    }

                    vals['product_tmpl_id'] = self.product_id;
                    /*
                    new Model("product.template").call("add_lot_serials", [
                        [], vals
                    ], {}, { async: false })
                    */
                    rpc.query({
                            model: "product.template",
                            method: 'add_lot_serials',
                            args: [
                                [], vals
                            ]
                        })
                        .then(function(res) {
                            if (res) {
                                self.prod_prod['tracking'] = 'serial'
                                self.add_product_with_lot(self.prod_prod, vals['codigo_battery'], res);

                            }
                        }).fail(function(error, event) {
                            event.preventDefault();
                            self.gui.show_popup('error', {
                                'title': _t("Error"),
                                'body': _t(error.data.message),
                            });
                        });
                }
                $('#search').val("");
                return true;
            } else {
                $('table.product-input-table input.name').css('border', 'thin solid red');
                alert("Product name is required");
                $('table.product-input-table input.name').focus();
                return false;
            }
        },
    });

    gui.define_screen({ name: 'productlist', widget: ProductListScreenWidget });

    var OrderListScreenWidget = screens.ScreenWidget.extend({
        template: 'OrderListScreenWidget',
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.reload_btn = function() {
                $('.fa-refresh').toggleClass('rotate', 'rotate-reset');
                self.reload_orders();
            };
        },
        show: function() {
            var self = this;
            this._super();

            this.renderElement();
            this.details_visible = false;
            this.$('.back').click(function() {
                self.gui.back();
            });
            this.reload_orders();
            this.$('.order-list-contents').delegate('.order-line', 'click', function(event) {
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });
            var search_timeout = null;

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress', function(event) {
                clearTimeout(search_timeout);

                var query = this.value;

                search_timeout = setTimeout(function() {
                    self.perform_search(query, event.which === 13);
                }, 70);
            });

            this.$('.searchbox .search-clear').click(function() {
                self.clear_search();
            });
        },
        renderElement: function() {
            var self = this;
            self._super();
            self.el.querySelector('.button.reload').addEventListener('click', this.reload_btn);
        },
        perform_search: function(query, associate_result) {
            var orders;
            if (query) {
                orders = this.pos.db.search_order(query);
                this.display_client_details('hide');
                this.render_list(orders);
            } else {
                var orders = self.pos.get('pos_order_list');
                this.render_list(orders);
            }
        },
        clear_search: function() {
            var orders = self.pos.get('pos_order_list');
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        render_list: function(orders) {
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                var order = orders[i];
                var orderline_html = QWeb.render('OrderLine', { widget: this, order: order });
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            }
            $("table.order-list").simplePagination({
                previousButtonClass: "btn btn-danger",
                nextButtonClass: "btn btn-danger",
                previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
                nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
                perPage: 10,
            });
        },
        line_select: function(event, $line, id) {
            var order = this.pos.db.get_order_by_id(id);
            this.$('.order-list .lowlight').removeClass('lowlight');
            if ($line.hasClass('highlight')) {
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.display_client_details('hide', order);
            } else {
                this.$('.order-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_client_details('show', order, y);
            }
        },
        reload_orders: function() {
            var self = this;
            //new Model('pos.order').call('ac_pos_search_read', [self.pos.order_domain], {}, { async: false })
            rpc.query({
                model: "pos.order",
                method: "ac_pos_search_read",
                args: [self.pos.order_domain]
            }).then(function(orders) {
                self.pos.db.add_orders(orders);
                self.pos.set({ 'pos_order_list': orders });
                self.render_list(self.pos.get('pos_order_list'));
            });
        },
        get_order_details: function(order_id) {
            var self = this;
            /*
            new Model('pos.order.line').call('search_read', [
                    [
                        ['order_id', '=', order_id]
                    ]
                ], {}, { async: false })
                */
            rpc.query({
                model: "pos.order.line",
                method: "search_read",
                args: [
                    [
                        ['order_id', '=', order_id]
                    ]
                ]
            }).then(function(pos_orderlines) {
                if (pos_orderlines) {
                    self.pos_orderlines = pos_orderlines;
                    _.each(pos_orderlines, function(line) {
                        self.pos.line_by_id[line.id] = line;
                    });
                }
            });
            /*
            new Model('account.bank.statement.line').call('search_read', [
                    [
                        ['pos_statement_id', '=', order_id]
                    ]
                ], {}, { async: false })
                */
            rpc.query({
                model: "account.bank.statement.line",
                method: "search_read",
                args: [
                    [
                        ['pos_statement_id', '=', order_id]
                    ]
                ]
            }).then(function(statement_ids) {
                if (statement_ids) {
                    self.statement_ids = statement_ids;
                }
            })
        },
        get_tax_by_id: function(orderline) {
            if (orderline) {
                var self = this;
                if (orderline.tax_ids_after_fiscal_position) {
                    var taxes = '';
                    _.each(orderline.tax_ids_after_fiscal_position, function(line_tax) {
                        var tax_by_id = self.pos.taxes_by_id[line_tax]
                        if (tax_by_id) {
                            taxes += tax_by_id.name + ", "
                        }
                    })
                    return taxes;
                }
            }
            return '';
        },
        validate_order_return: function(order_id) {
            var self = this;
            var tobe_return_order = self.pos.db.get_order_by_id(order_id);
            if (tobe_return_order.return_status === "full") {
                alert("Already returned order");
                return
            }
            if (tobe_return_order && self.pos_orderlines) {
                self.pos.gui.show_popup('line_return_popup', {
                    order_id: order_id,
                    lines: self.pos_orderlines,
                });
            }
        },
        display_client_details: function(visibility, order, clickpos) {
            var self = this;
            var contents = this.$('.order-details-contents');
            var parent = this.$('.order-list').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();

            contents.off('click', '.button.close');
            contents.off('click', '.button.return');
            contents.on('click', '.button.close', function() {
                self.display_client_details('hide');
            });
            contents.on('click', '.button.return', function() {
                self.validate_order_return(order.id);
            });

            if (visibility === 'show') {
                contents.empty();
                self.get_order_details(order.id);

                contents.append($(QWeb.render('OrderDetails', {
                    widget: this,
                    order: order,
                    orderlines: self.pos_orderlines || false,
                    statement_ids: self.statement_ids || false,
                })));
                if (order.return_status === "full") {
                    $('.button.return').removeClass('highlight');
                }
                var new_height = contents.height();

                if (!this.details_visible) {
                    // resize client list to take into account client details
                    parent.height('-=' + new_height);

                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
            } else if (visibility === 'hide') {
                contents.empty();
                parent.height('100%');
                if (height > scroll) {
                    contents.css({ height: height + 'px' });
                    contents.animate({ height: 0 }, 400, function() {
                        contents.css({ height: '' });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
            }
        },
    });
    gui.define_screen({ name: 'orderlist', widget: OrderListScreenWidget });

});