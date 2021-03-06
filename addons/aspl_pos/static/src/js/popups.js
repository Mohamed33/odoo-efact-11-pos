odoo.define('aspl_pos.popups', ["point_of_sale.popups", "point_of_sale.gui", "web.rpc", "point_of_sale.models", "web.core"], function(require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    //var Model = require('web.DataModel');
    var rpc = require('web.rpc');
    var models = require('point_of_sale.models');
    var core = require('web.core');

    var _t = core._t;

    var SaleOrderPopupWidget = PopupWidget.extend({
        template: 'SaleOrderPopupWidget',
    });
    gui.define_popup({ name: 'saleOrder', widget: SaleOrderPopupWidget });

    var ProductSerialListPopup = PopupWidget.extend({
        template: 'ProductSerialListPopup',
        show: function(options) {
            var self = this;
            options = options || {};
            this._super(options);
            this.product_id = options.product_id || false;
            self.name_list = [];
            //console.log(options);
            //console.log([self.product_id, self.pos.config.stock_location_id[0]])
            $(".o_loading").show()
            if (this.product_id) {
                /*
                new Model('stock.production.lot').call('get_qty_location', [self.product_id, self.pos.config.stock_location_id[0]], {}, { async: false })
                */
                //console.log([self.product_id, self.pos.config.stock_location_id[0]])
                rpc.query({
                    model: 'stock.production.lot',
                    method: 'get_qty_location',
                    args: [self.product_id, self.pos.config.stock_location_id[0]]
                }).then(function(serials) {
                    self.serials = serials;
                    _.each(self.serials, function(serial) {
                        self.name_list.push(serial.name);
                    });
                    self.temp_serials = self.serials;
                    self.renderElement();
                    $("table.serial_list_table").show()
                    $(".cancel").show()
                    $(".o_loading").hide()
                });
            }

        },
        validate_serial: function(serial) {
            var self = this;
            var order = self.pos.get_order();
            if (serial) {
                var orderlines = order.get_orderlines();
                if (orderlines.length > 0) {
                    var temp = _.findWhere(orderlines, { 'prodlot_id_id': serial.id })
                    if (temp) {
                        return false;
                    }
                }
                return true;
            }
        },
        renderElement: function() {
            var self = this;
            var order = self.pos.get_order();
            this._super();
            $("table.serial_list_table").simplePagination({
                previousButtonClass: "btn btn-danger",
                nextButtonClass: "btn btn-danger",
                previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
                nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
                perPage: 10,
            });
            $("table.serial_list_table").hide()
            console.log("Ocultar cancel")
            $(".cancel").hide()
            $(".o_loading").show()
            $('.serial_list_table tbody').find('tr').click(function() {
                var line_qty = 1;
                console.log("mostrar cancel")

                var selected_serial_record = self.find_serial_record_by_id($(this).data('id'));
                if (selected_serial_record) {
                    var temp = true;
                    var sr_no = selected_serial_record.name;
                    var product = self.pos.db.get_product_by_id(self.product_id);
                    var line = new models.Orderline({}, { pos: self.pos, order: order, product: product });
                    if (selected_serial_record.remaining_qty) {
                        line.set_remainig_lot(selected_serial_record.remaining_qty);
                    }
                    line.set_serial_id(selected_serial_record.id);
                    line.set_serial(selected_serial_record.name);
                    line.set_input_lot_serial(selected_serial_record.name, 1);
                    var orderlines = order.get_orderlines();
                    _.each(orderlines, function(item) {
                        if (item.get_product().tracking == 'lot' && item.get_product().id == self.product_id &&
                            item.get_serial() == selected_serial_record.name) {
                            line_qty += item.get_quantity();
                        }
                        if (item.get_product().tracking != 'lot' && item.get_product().id == self.product_id &&
                            item.get_serial() == selected_serial_record.name) {
                            alert('Same product is already assigned with same serial number !');
                            sr_no = null;
                            temp = false;
                            return temp;
                        }

                    });
                    if (temp) {
                        if (selected_serial_record.remaining_qty < line_qty) {
                            alert('Not allow more than ' + selected_serial_record.remaining_qty + ' quantity');
                            sr_no = null;
                            return false;
                        }
                        var last_orderline = order.get_last_orderline();
                        if (last_orderline && last_orderline.can_be_merged_with(line)) {
                            last_orderline.merge(line);
                        } else {
                            order.orderlines.add(line);
                        }
                        order.select_orderline(order.get_last_orderline());
                    }
                    self.gui.close_popup();
                }
            });
            $('.serial_search_box').find('.txt_serial_input').keypress(function(e) {
                $('.txt_serial_input').autocomplete({
                    source: self.name_list,
                    select: function(event, ui) {
                        var input = $('.txt_serial_input');
                        self.serials = [_.find(self.temp_serials, function(o) {
                            return o.name === input.val()
                        })];
                        self.renderElement();
                    }
                });
                if (e.which === 13) {
                    var input = $(this);
                    self.serials = [_.find(self.temp_serials, function(o) {
                        return o.name === input.val()
                    })];
                    self.renderElement();
                }
            });
        },
        find_serial_record_by_id: function(id) {
            var self = this;
            return _.find(self.serials, function(o) { return o.id == id; })
        },
    });
    gui.define_popup({ name: 'product_serial_list_popup', widget: ProductSerialListPopup });

    var LineReturnPopup = PopupWidget.extend({
        template: 'LineReturnPopup',
        show: function(options) {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            this.lines = options.lines || false;
            this.order_id = options.order_id || false;
            this.renderElement();
        },
        click_confirm: function() {
            var self = this;
            var order = this.pos.get_order();
            var returning = false;
            var return_order = self.pos.db.get_order_by_id(this.order_id);
            _.each($('.popup-orderline-list-contents').find('tr'), function(popup_lines) {
                if ($(popup_lines).find('.return_qty').val() > 0 && $(popup_lines).find('.check_return').prop('checked')) {
                    var return_qty = $(popup_lines).find('.return_qty').val();
                    var line_id = $(popup_lines).data('line-id');
                    var line = self.pos.line_by_id[line_id];
                    if (line) {
                        var product = self.pos.db.get_product_by_id(line.product_id[0]);
                        if (product) {
                            returning = true;
                            order.set_return_order(true);
                            order.add_product(product, { quantity: return_qty * -1, price: line.price_unit })
                            order.get_selected_orderline().set_return_quantity(return_qty * -1);
                            order.get_selected_orderline().set_oid(line.order_id);
                            order.get_selected_orderline().set_back_order(return_order.pos_reference);
                            order.get_selected_orderline().set_serial_id(line.prodlot_id ? line.prodlot_id[0] : null);
                            order.get_selected_orderline().set_serial(line.prodlot_id ? line.prodlot_id[1] : null);
                            order.get_selected_orderline().set_input_lot_serial(line.prodlot_id[1], return_qty);
                            order.get_selected_orderline().set_stock_income(true);
                        }
                    }
                }
            });
            if (returning) {
                if (return_order) {
                    if (return_order.partner_id) {
                        var partner = self.pos.db.get_partner_by_id(return_order.partner_id[0]);
                        if (partner) {
                            order.set_client(partner);
                        }
                    }
                }
                if (self.pos.config.so_operation_draft)
                    self.pos.gui.screen_instances.products.action_buttons.QuotationButton.hide()
                if (self.pos.config.so_operation_confirm)
                    self.pos.gui.screen_instances.products.action_buttons.ConfirmButton.hide()
                if (self.pos.config.so_operation_paid)
                    self.pos.gui.screen_instances.payment.renderElement();
                self.gui.show_screen('payment');
            }
        },
        renderElement: function() {
            var self = this;
            this._super();
            $('.return_qty').keyup(function(e) {
                if (/\D/g.test(this.value)) {
                    alert("Invalid input");
                    this.value = this.value.replace(/\D/g, '');
                    return
                }
                var line_id = $(this).data('line-id')
                if (line_id) {
                    var line = self.pos.line_by_id[line_id];
                    if (line) {
                        var input_val = $(this).val() ? parseInt($(this).val()) : 0;
                        if (input_val < 0 || input_val > (line.return_qty)) {
                            alert("Invalid Quantity");
                            $(this).val(0);
                        } else if (input_val == 0) {
                            $(this).val(0);
                        }
                    }
                }
            });
            $('.complete_return').click(function() {
                $('.check_return').prop('checked', true).trigger('change');
            });
            $('.check_return').change(function() {
                var line_id = $(this).data('line-id');
                var line = self.pos.line_by_id[line_id];
                if ($(this).prop('checked')) {
                    $('.return_qty[data-line-id="' + line_id + '"]').val(line.qty)
                    if (line && line.prodlot_id.length > 0) {
                        $('.return_qty[data-line-id="' + line_id + '"]').prop('disabled', true);
                    }
                } else {
                    $('.return_qty[data-line-id="' + line_id + '"]').val('')
                    if (line && line.prodlot_id.length > 0) {
                        $('.return_qty[data-line-id="' + line_id + '"]').prop('disabled', false);
                    }
                }
            })
        }
    });
    gui.define_popup({ name: 'line_return_popup', widget: LineReturnPopup });
});