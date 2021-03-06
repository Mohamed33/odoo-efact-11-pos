odoo.define('aspl_pos.models', ['web.core', 'point_of_sale.models', 'point_of_sale.popups', 'web.rpc'], function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    //var Model = require('web.DataModel');
    var rpc = require('web.rpc');
    var _t = core._t;

    models.PosModel.prototype.models.push({
        model: 'product.category',
        fields: ['id', 'display_name'],
        domain: null,
        loaded: function(self, product_category) {
            self.product_category = [];
            self.product_category = product_category;
        },
    });

    models.load_fields("product.product", ['categ_id', 'standard_price', 'name', 'taxes_id', 'type', 'tracking', 'codigo_battery', 'non_refundable']);

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        load_server_data: function() {
            var self = this;
            var loaded = _super_posmodel.prototype.load_server_data.call(this);
            self.line_by_id = [];
            loaded = loaded.then(function() {
                self.order_domain = [
                    ['state', 'not in', ['cancel']],
                    ['back_order', '=', false]
                ];
                if (self.config.load_current_session_order) {
                    self.order_domain.push(['session_id', '=', self.pos_session.id]);
                    self.order_domain.push(['state', '!=', 'posted']);
                }
                if (self.config.specified_orders) {
                    var date = new Date();
                    var start_date;
                    if (date) {
                        if (self.config.last_days) {
                            date.setDate(date.getDate() - self.config.last_days);
                        }
                        start_date = date.toJSON().slice(0, 10);
                        self.order_domain.push(['create_date', '>=', start_date]);
                    }
                }
                //return new Model('pos.order').get_func('ac_pos_search_read')(self.order_domain)


                return rpc.query({
                        model: "pos.order",
                        method: "ac_pos_search_read",
                        args: [self.order_domain]
                    })
                    .then(function(orders) {
                        self.db.add_orders(orders);
                        self.set({ 'pos_order_list': orders });
                    });
            });
            return loaded;
        },
        _save_to_server: function(orders, options) {
            if (!orders || !orders.length) {
                var result = $.Deferred();
                result.resolve([]);
                return result;
            }

            options = options || {};

            var self = this;
            var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;

            // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
            // then we want to notify the user that we are waiting on something )
            /*
            var posOrderModel = new Model('pos.order');
            return posOrderModel.call('create_from_ui', [_.map(orders, function(order) {
                    order.to_invoice = options.to_invoice || false;
                    return order;
                })],
                undefined, {
                    shadow: !options.to_invoice,
                    timeout: timeout
                }
            )*/
            return rpc.query({
                    model: 'pos.order',
                    method: 'create_from_ui',
                    args: [_.map(orders, function(order) {
                        order.to_invoice = options.to_invoice || false;
                        return order;
                    })]
                })
                .then(function(server_ids) {
                    if (server_ids != []) {
                        /*
                        new Model('pos.order').get_func('ac_pos_search_read')([
                                ['id', 'in', server_ids],
                                ['back_order', '=', false]
                            ])
                            */
                        rpc.query({
                            model: 'pos.order',
                            method: 'ac_pos_search_read',
                            args: [
                                [
                                    ['id', 'in', server_ids],
                                    ['back_order', '=', false]
                                ]
                            ]
                        }).then(function(orders) {
                            var orders_data = self.get('pos_order_list');
                            var new_orders = [];
                            var flag = true;
                            if (orders && orders[0]) {
                                for (var i in orders_data) {
                                    if (orders_data[i].pos_reference == orders[0].pos_reference) {
                                        new_orders.push(orders[0])
                                        flag = false
                                    } else {
                                        new_orders.push(orders_data[i])
                                    }
                                }
                                if (flag) {
                                    new_orders = orders.concat(orders_data);
                                }
                                self.db.add_orders(new_orders);
                                self.set({ 'pos_order_list': new_orders });
                            } else {
                                new_orders = orders.concat(orders_data);
                                self.db.add_orders(new_orders);
                                self.set({ 'pos_order_list': new_orders });
                            }
                        });
                    }
                    _.each(orders, function(order) {
                        self.db.remove_order(order.id);
                    });
                    return server_ids;
                }).fail(function(error, event) {
                    if (error.code === 200) { // Business Logic Error, not a connection problem
                        self.gui.show_popup('error-traceback', {
                            message: error.data.message,
                            comment: error.data.debug
                        });
                    }
                    // prevent an error popup creation by the rpc failure
                    // we want the failure to be silent as we send the orders in the background
                    event.preventDefault();
                    console.error('Failed to send orders:', orders);
                });
        },
    });

    var orderline_id = 1;
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            this.oid = null;
            this.prodlot_id = null;
            this.prodlot_id_id = null;
            this.remainig_lot = 0;
            this.dont_remove = false;
            this.operation_product = false;
            this.stock_income = false;
            _super_orderline.initialize.call(this, attr, options);
        },
        export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var return_process = this.get_oid();
            var new_val = {
                prodlot_id: this.get_serial_id() || false,
                return_qty: this.get_quantity() || false,
                return_process: return_process,
                exchange_product: this.get_exchange_product() || false,
                operation_product: this.get_operation_product() || false,
                stock_income: this.get_stock_income() || false,
            }
            $.extend(lines, new_val);
            return lines;
        },
        can_be_merged_with: function(orderline) {
            var merged_lines = _super_orderline.can_be_merged_with.call(this, orderline);
            if (this.get_serial() && orderline.get_product().tracking !== 'lot') {
                return false;
            }
            if (this.get_serial() != orderline.get_serial()) {
                return false;
            }
            return merged_lines;
        },
        set_serial_id: function(sr_no_id) {
            this.prodlot_id_id = sr_no_id;
        },
        get_serial_id: function() {
            return this.prodlot_id_id;
        },
        set_serial: function(sr_no) {
            this.prodlot_id = sr_no;
        },
        get_serial: function() {
            return this.prodlot_id;
        },
        set_remainig_lot: function(qty) {
            this.remainig_lot = qty;
        },
        get_remainig_lot: function() {
            return this.remainig_lot;
        },
        set_input_lot_serial: function(serial_name, line_qty) {
            if (line_qty == "remove" || line_qty == "") {
                return
            }
            // Remove All Lots
            var pack_lot_lines = this.pack_lot_lines;
            var len = pack_lot_lines.length;
            var cids = [];
            for (var i = 0; i < len; i++) {
                var lot_line = pack_lot_lines.models[i];
                cids.push(lot_line.cid);
            }
            for (var j in cids) {
                var lot_model = pack_lot_lines.get({ cid: cids[j] });
                lot_model.remove();
            }
            // Add new lots
            for (var k = 0; k < line_qty; k++) {
                var lot_model = new models.Packlotline({}, { 'order_line': this });
                lot_model.set_lot_name(serial_name);
                if (pack_lot_lines) {
                    pack_lot_lines.add(lot_model);
                }
            }
            this.trigger('change', this);
        },
        set_return_quantity: function(return_quantity) {
            this.set('return_quantity', return_quantity);
        },
        get_return_quantity: function() {
            return this.get('return_quantity');
        },
        set_oid: function(oid) {
            this.set('oid', oid)
        },
        get_oid: function() {
            return this.get('oid');
        },
        set_back_order: function(backorder) {
            this.set('backorder', backorder);
        },
        get_back_order: function() {
            return this.get('backorder');
        },
        set_dont_remove: function(val) {
            this.dont_remove = val;
        },
        get_dont_remove: function(val) {
            return this.dont_remove;
        },
        has_valid_product_lot: function() {
            return _super_orderline.has_valid_product_lot.call(this) || this.get_dont_remove();
        },
        set_exchange_product: function(exchange_product) {
            this.exchange_product = exchange_product;
        },
        get_exchange_product: function() {
            return this.exchange_product;
        },
        set_operation_product: function(operation_product) {
            this.operation_product = operation_product;
        },
        get_operation_product: function() {
            return this.operation_product;
        },
        set_stock_income: function(stock_income) {
            this.stock_income = stock_income;
        },
        get_stock_income: function() {
            return this.stock_income;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            var self = this;
            _super_order.initialize.apply(this, arguments);
            this.receipt_type = 'receipt'; // 'receipt' || 'invoice'
            this.temporary = options.temporary || false;
            this.serial_list = [];
            this.from_product_operation = false;
            return this;
        },
        finalize: function() {
            var self = this;
            if (self.pos.config.so_operation_draft)
                self.pos.gui.screen_instances.products.action_buttons.QuotationButton.show()
            if (self.pos.config.so_operation_confirm)
                self.pos.gui.screen_instances.products.action_buttons.ConfirmButton.show()
            this.destroy();
        },
        generate_unique_id: function() {
            var timestamp = new Date().getTime();
            return Number(timestamp.toString().slice(-10));
        },
        set_serial_list: function(val) {
            this.serial_list.push(val);
        },
        get_serial_list: function() {
            return this.serial_list;
        },
        add_product: function(product, options) {
            var self = this;
            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new models.Orderline({}, { pos: this.pos, order: this, product: product });
            if (line.has_product_lot && this.pos.config.enable_pos_serial && !this.get_return_order()) {
                var lst = attr.order.get_serial_list() || [];
                setTimeout(function() {
                    if (product.id) {
                        self.pos.gui.show_popup('product_serial_list_popup', { product_id: product.id });
                    }

                }, 500);
            } else {
                _super_order.add_product.call(this, product, options);
            }
        },
        export_as_JSON: function() {
            var submitted_order = _super_order.export_as_JSON.call(this);
            var backOrders_list = [];
            _.each(this.get_orderlines(), function(item) {
                if (item.get_back_order()) {
                    if ($.inArray(item.get_back_order(), backOrders_list) == -1) {
                        backOrders_list.push(item.get_back_order());
                    }
                }
            });
            var unique_backOrders = backOrders_list.join(',');
            var new_val = {
                sale_order_name: this.get_sale_order_name() || false,
                back_order: unique_backOrders,
            }
            $.extend(submitted_order, new_val);
            return submitted_order;
        },
        set_sale_order_name: function(name) {
            this.set('sale_order_name', name);
        },
        get_sale_order_name: function() {
            return this.get('sale_order_name');
        },
        remove_orderline: function(line) {
            if (this.get_serial_list()) {
                var index = this.get_serial_list().indexOf(line.get_serial_id());
                this.get_serial_list().splice(index, 1);
            }
            _super_order.remove_orderline.apply(this, arguments);
        },
        set_return_order: function(return_order) {
            this.set('return_order', return_order);
        },
        get_return_order: function() {
            return this.get('return_order');
        },
        set_from_product_operation: function(from_product_operation) {
            this.from_product_operation = from_product_operation
        },
        get_from_product_operation: function() {
            return this.from_product_operation
        },
    });
});