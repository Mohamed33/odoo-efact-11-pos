odoo.define('pos_journal_sequence.pos_journal_sequence', 
    ['point_of_sale.models', 'point_of_sale.screens', 'point_of_sale.DB', 'web.core', "web.rpc", 'point_of_sale.BaseWidget'], 
function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PosDB = require('point_of_sale.DB');
    var core = require('web.core');
    var rpc = require("web.rpc")
        //var Model = require('web.DataModel');
    var BaseWidget = require('point_of_sale.BaseWidget');
    var QWeb = core.qweb;

    var _t = core._t;

    var PosModelSuper = models.PosModel;
    var PosDBSuper = PosDB;
    var OrderSuper = models.Order;
    var exports = {};
    
   
    BaseWidget.include({
        format_currency: function(amount, precision, type, simbolo_moneda) {
            var currency = (this.pos && this.pos.currency) ? this.pos.currency : { symbol: '$', position: 'after', rounding: 0.01, decimals: 2 };

            amount = this.format_currency_no_symbol(amount, precision);

            if (currency.position === 'after') {
                if (simbolo_moneda) {
                    var amount = amount + ' ' + (currency.symbol || '')
                }

            } else {
                if (simbolo_moneda) {
                    var amount = (currency.symbol || '') + ' ' + amount;
                }
            }

            if (type == "total") {
                return amount.toString().substr(0, amount.toString().length)
            } else {
                return amount
            }
        }
    })

    PosDB = PosDB.extend({
        init: function(options) {
            this.journal_by_id = {};
            this.sequence_by_id = {};
            this.journal_sequence_by_id = {};
            //this.invoice_numbers=[];
            return PosDBSuper.prototype.init.apply(this, arguments);
        },
        add_invoice_numbers: function(number) {
            if (number) {
                var invoice_numbers = this.load('invoice_numbers') || [];
                invoice_numbers.push(number);
                this.save('invoice_numbers', invoice_numbers || null);
            }
        },
        get_invoice_numbers: function() {
            return this.load('invoice_numbers') || [];
        },
        add_journals: function(journals) {
            if (!journals instanceof Array) {
                journals = [journals];
            }
            for (var i = 0, len = journals.length; i < len; i++) {
                this.journal_by_id[journals[i].id] = journals[i];
                this.journal_sequence_by_id[journals[i].id] = journals[i].sequence_id[0];
            }
        },
        add_sequences: function(sequences) {
            if (!sequences instanceof Array) {
                sequences = [sequences];
            }
            for (var i = 0, len = sequences.length; i < len; i++) {
                this.sequence_by_id[sequences[i].id] = sequences[i];
            }
        },
        get_journal_sequence_id: function(journal_id) {
            var sequence_id = this.journal_sequence_by_id[journal_id]
            return this.sequence_by_id[sequence_id] || {};
        },
        get_journal_id: function(journal_id) {
            return this.journal_by_id[journal_id];
        },
        set_sequence_next: function(id, number_increment) {
            var sequences = this.load('sequences') || {};
            sequences[id] = number_increment + 1;
            this.save('sequences', sequences || null);
        },
        get_sequence_next: function(journal_id) {
            var sequence_id = this.journal_sequence_by_id[journal_id];

            var sequences = this.load('sequences') || {};
            if (sequences[sequence_id]) {
                if (this.sequence_by_id[sequence_id].all_number_increment > sequences[sequence_id]) {
                    return this.sequence_by_id[sequence_id].all_number_increment;
                } else {
                    return sequences[sequence_id];
                }
            } else {
                return this.sequence_by_id[sequence_id].all_number_increment;
            }
        },
    });

    //INICIO AGREGADO
    var index = -1;
    for (var i = 0; i < PosModelSuper.prototype.models.length; i++) {
        if (PosModelSuper.prototype.models[i].model == 'res.partner') {
            index = i;
        }
    }
    if (index > -1) {
        PosModelSuper.prototype.models[index].fields.push('tipo_documento');
    }
    //FIN AGREGADO

    PosModelSuper.prototype.models.push({
        model: 'account.journal',
        fields: [],
        domain: function(self) {
            return [
                ['id', 'in', self.config.invoice_journal_ids]
            ];
        },
        loaded: function(self, journals) {
            var sequence_ids = [];
            for (var i = 0, len = journals.length; i < len; i++) {
                sequence_ids.push(journals[i].sequence_id[0]);
            }
            self.journal_ids = journals;
            self.sequence_ids = sequence_ids;
            self.db.add_journals(journals);
        },
    });
    PosModelSuper.prototype.models.push({
        model: 'ir.sequence',
        fields: ['id', 'interpolated_prefix', 'interpolated_suffix', 'padding', 'all_number_increment'],
        domain: function(self) {
            return [
                ['id', 'in', self.sequence_ids]
            ];
        },
        loaded: function(self, sequences) {
            self.db.add_sequences(sequences);
        },
    });
    PosModelSuper.prototype.models[2].fields.push("logo");
    PosModelSuper.prototype.models[2].fields.push("street");
    PosModelSuper.prototype.models[2].fields.push("phone");


    var model_account_tax = _.find(PosModelSuper.prototype.models,function(model){return model.model=="account.tax"})
    model_account_tax.fields.push("tipo_afectacion_igv")
    model_account_tax.fields.push("tipo_afectacion_igv_code")
    //PosModelSuper.prototype.models[7].push("tipo_afectcion_igv")
    //PosModelSuper.prototype.models[7].push("tipo_afectcion_igv_code")

    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            var res = PosModelSuper.prototype.initialize.apply(this, arguments);
            this.db = new PosDB(); // a local database used to search trough products and categories & store pending orders
            return res;
        },
        generate_order_number: function(journal_id) {
            var sequence = this.db.get_journal_sequence_id(journal_id);
            var num = "%0" + sequence.padding + "d";
            var prefix = sequence.interpolated_prefix || "";
            var suffix = sequence.interpolated_suffix || "";
            var increment = this.db.get_sequence_next(journal_id);
            var number = prefix + num.sprintf(parseInt(increment)) + suffix;
            return { 'number': number, 'sequence_number': increment };
        },
        get_order_number: function(journal_id) {
            var numbers = this.generate_order_number(journal_id);
            if (this.db.get_invoice_numbers().indexOf(numbers.number) != -1) {
                var numbers = this.get_order_number(journal_id);
                var sequence = this.db.get_journal_sequence_id(journal_id);
                this.db.set_sequence_next(sequence.id, numbers.sequence_number);
            }
            return numbers;
        },
        set_sequence: function(journal_id, number, number_increment) {
            var sequence = this.db.get_journal_sequence_id(journal_id);
            this.db.set_sequence_next(sequence.id, number_increment);
            this.db.add_invoice_numbers(number);

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

            // Keep the order ids that are about to be sent to the
            // backend. In between create_from_ui and the success callback
            // new orders may have been added to it.
            var order_ids_to_sync = _.pluck(orders, 'id');

            // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
            // then we want to notify the user that we are waiting on something )
            /*
            return posOrderModel.call('create_from_ui', [_.map(orders, function(order) {
                    order.to_invoice = options.to_invoice || false;
                    return order;
                })],
                undefined, {
                    shadow: !options.to_invoice,
                    timeout: timeout
                }
            ).
            */
            return rpc.query({
                model: "pos.order",
                method: "create_from_ui",
                args: [_.map(orders, function(order) {
                    // order.to_invoice = options.to_invoice || false;
                    order.to_invoice = order.data.invoice_type_code_id?true:false
                    return order;
                })]
            }).then(function(server_ids) {
                _.each(order_ids_to_sync, function(order_id) {
                    self.db.remove_order(order_id);
                });
                self.set('failed', false);
                return server_ids;
            }).fail(function(error, event) {
                if (error.code === 200) { // Business Logic Error, not a connection problem
                    //if warning do not need to display traceback!!
                    if (error.data.exception_type == 'warning') {
                        delete error.data.debug;
                    }

                    // Hide error if already shown before ...
                    if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
                        self.gui.show_popup('error-traceback', {
                            'title': error.data.message,
                            'body': error.data.debug
                        });
                    }
                    self.set('failed', error)
                }
                // prevent an error popup creation by the rpc failure
                // we want the failure to be silent as we send the orders in the background
                event.preventDefault();
                console.error('Failed to send orders:', orders);
            });
        }
    });

    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            var res = OrderSuper.prototype.initialize.apply(this, arguments);
            this.number = false;
            this.journal_id = false;
            this.sequence_number = 0;
            return res;
        },
        set_sale_journal: function(journal_id) {
            this.assert_editable();
            this.journal_id = journal_id;
        },
        get_sale_journal: function() {
            return this.journal_id;
        },
        export_as_JSON: function() {
            var res = OrderSuper.prototype.export_as_JSON.apply(this, arguments);

            var journal = this.pos.db.get_journal_id(this.journal_id);
            res['invoice_journal'] = this.journal_id;
            res['number'] = this.number;
            res['sequence_number'] = this.sequence_number;
            res['invoice_type_code_id'] = (typeof journal === "undefined") ? journal : journal.invoice_type_code_id;
            /*if (this.journal_id){
                res['to_invoice']= true;
            }*/
            return res;
        },
        set_number: function(number) {
            this.assert_editable();
            this.number = number;
        },
        get_number: function() {
            return this.number;
        },
        set_sequence_number: function(number) {
            this.assert_editable();
            this.sequence_number = number;
        },
        get_sequence_number: function() {
            return this.sequence_number;
        },
    });

    exports.models =models

    screens.PaymentScreenWidget.include({

        validate_order: function(force_validation) {
            self = this;
            this._super(force_validation);
        },
        renderElement: function() {
            var self = this;
            this._super();
            var sale_journals = this.render_sale_journals();
            sale_journals.appendTo(this.$('.payment-buttons'));
            this.$('.js_sale_journal').click(function() {
                self.click_sale_journals($(this).data('id'));
            });
        },
        render_sale_journals: function() {
            var self = this;
            var sale_journals = $(QWeb.render('SaleInvoiceJournal', { widget: this }));
            return sale_journals;
        },
        click_sale_journals: function(journal_id) {
            var order = this.pos.get_order();
            if (order.get_sale_journal() != journal_id) {
                order.set_sale_journal(journal_id);
                this.$('.js_sale_journal').removeClass('highlight');
                this.$('div[data-id="' + journal_id + '"]').addClass('highlight');
            } else {
                order.set_sale_journal(false);
                this.$('.js_sale_journal').removeClass('highlight');
            }

        },
        validate_journal_invoice: function() {
            var res = false;
            var order = this.pos.get_order();

            if (!order.get_client() && this.pos.config.anonymous_id) {
                var new_client = this.pos.db.get_partner_by_id(this.pos.config.anonymous_id[0]);
                if (new_client) {
                    order.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                        return fp.id === new_client.property_account_position_id[0];
                    });
                } else {
                    order.fiscal_position = undefined;
                }
                if (new_client) {
                    order.set_client(new_client);
                }
            }
            if (!order.get_client() && order.get_sale_journal()) {

                self.gui.show_popup('confirm', {
                    'title': _t('An anonymous order cannot be invoiced'),
                    'body': _t('You need to select the customer before you can invoice an order.'),
                    confirm: function() {
                        self.gui.show_screen('clientlist');
                    },
                });
                return true;
            }
            return res;
        },
        order_is_valid: function(force_validation) {
            var res = this._super(force_validation);
            if (!res) {
                return res;
            }
            var order = this.pos.get_order();
            if (order.get_sale_journal()) {
                var numbers = this.pos.get_order_number(order.get_sale_journal());
                order.set_number(numbers.number);
                order.set_sequence_number(numbers.sequence_number);
            }
            if (order.get_number() && !order.get_sale_journal()) {
                order.set_number(false);
                order.set_sequence_number(0);
            }
            if (order.get_number()) {
                this.pos.set_sequence(order.get_sale_journal(), order.get_number(), order.get_sequence_number())
            }
            return res;
        },
        rucValido: function(ruc) {
            var ex_regular_ruc;
            ex_regular_ruc = /^\d{11}(?:[-\s]\d{4})?$/;
            if (ex_regular_ruc.test(ruc)) {
                return true
            }
            return false;
        },
        dniValido: function(dni) {
            var ex_regular_dni;
            ex_regular_dni = /^\d{8}(?:[-\s]\d{4})?$/;
            if (ex_regular_dni.test(dni)) {
                return true
            }
            return false;
        },
        validate_order: function(force_validation) {
            self = this;
            var order = this.pos.get_order();
            var client = order.get_client();

            var journal = _.filter(order.pos.journal_ids, function(j_id) {
                return j_id["id"] == order.journal_id
            })[0]
            var total = 0;
            var error_msg_subtotal = ""
            order["orderlines"]["models"].forEach(function(orderline,index) {
                var subtotal = orderline["quantity"] * orderline["price"] * (1-orderline["discount"]/100.0)
                total += subtotal
                if(subtotal<=0){
                    error_msg_subtotal +=" * item ("+(index+1).toString()+") - ["+orderline["product"]["default_code"]+"]"+orderline["product"]["display_name"]
                }
            })
            

            if (journal) {
                if (client) {
                    let tipo_documento = client["tipo_documento"];
                    if (!tipo_documento) {
                        self.gui.show_popup('confirm', {
                            'title': _t('Datos del Cliente Incorrectos'),
                            'body': _t('El cliente seleccionado no tiene un tipo de documento identidad. Tipos de Documento: 1 - DNI, 6 - RUC y "-" (guión) para ventas Menores a S/.700.00 '),
                            confirm: function() {
                                self.gui.show_screen('clientlist');
                            },
                        });
                        return true
                    }
                }
                if(journal["invoice_type_code_id"] == '03' || journal["invoice_type_code_id"] == '01'){
                    if(error_msg_subtotal.length>0){
                        self.gui.show_popup('confirm', {
                            'title': 'Error: Cantidad y precio de uno o más productos deben ser mayores a cero.',
                            'body': $('<div>Revise los siguientes productos de la lista de pedido:'+error_msg_subtotal+"</div>").html(),
                            confirm: function() {
                                self.gui.show_screen('products');
                            },
                        });
                        return true
                    }
                }
                if (journal["invoice_type_code_id"] == '03') {
                    if (client) {
                        let name = client["name"];
                        let dni = client["vat"];
                        let tipo_documento = client["tipo_documento"];

                        if (total >= 700) {
                            if (!dni) {
                                self.gui.show_popup('confirm', {
                                    'title': _t('Datos del Cliente Incorrectos'),
                                    'body': _t('El número de documento de identidad del cliente es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 el detalle de DNI es obligatorio '),
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return true
                            }
                            if (!tipo_documento) {
                                self.gui.show_popup('confirm', {
                                    'title': _t('Datos del Cliente Incorrectos'),
                                    'body': _t('El tipo de documento de identidad es obligatorio'),
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return true
                            }
                            if (tipo_documento != "1") {
                                self.gui.show_popup('confirm', {
                                    'title': _t('Datos del Cliente Incorrectos'),
                                    'body': _t('El tipo de documento de identidad (DNI) es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 de detalle el DNI es obligatorio'),
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return true
                            }
                            if (!self.dniValido(dni)) {
                                self.gui.show_popup('confirm', {
                                    'title': _t('Error'),
                                    'body': _t('El DNI del cliente tiene un formato incorrecto.'),
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return true
                            }
                        }
                    } else {
                        self.gui.show_popup('confirm', {
                            'title': _t('No ha seleccionado un cliente'),
                            'body': _t('Seleccione un cliente'),
                            confirm: function() {
                                self.gui.show_screen('clientlist');
                            },
                        });
                        return true
                    }
                } else if (journal["invoice_type_code_id"] == '01') {
                    if (client) {
                        let name = client["name"];
                        let ruc = client["vat"];
                        let street = client["street"];
                        let tipo_documento = client["tipo_documento"]
                        let email = client["email"]
                        if (!ruc) {
                            self.gui.show_popup('confirm', {
                                'title': _t('Datos del Cliente Incorrectos'),
                                'body': _t('El número de documento de identidad del cliente es obligatorio'),
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return true
                        }
                        if (!tipo_documento) {
                            self.gui.show_popup('confirm', {
                                'title': _t('Datos del Cliente Incorrectos'),
                                'body': _t('El tipo de documento de identidad es obligatorio'),
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return true
                        }
                        if (tipo_documento != "6") {
                            self.gui.show_popup('confirm', {
                                'title': _t('Datos del Cliente Incorrectos'),
                                'body': _t('Para emitir una Factura el cliente seleccionada debe tener RUC'),
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return true
                        }
                        if (!self.rucValido(ruc)) {
                            self.gui.show_popup('confirm', {
                                'title': _t('Datos del Cliente Incorrectos'),
                                'body': _t('El Número de documento de identidad del cliente (RUC) no es válido.'),
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return true
                        }
                    } else {
                        self.gui.show_popup('confirm', {
                            'title': _t('No ha seleccionado un cliente'),
                            'body': _t('Seleccione un cliente. Recuerde que para una factura el cliente asociado debe poseer RUC y debe estar Activo.'),
                            confirm: function() {
                                self.gui.show_screen('clientlist');
                            },
                        });
                        return true
                    }
                }
            }

            if (this.validate_journal_invoice()) {
                return;
            }
            this._super(force_validation);

        },
    });

    exports.screens= screens

    return exports
});