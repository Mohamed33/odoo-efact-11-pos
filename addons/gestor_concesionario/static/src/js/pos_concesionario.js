odoo.define('gestor_concesionario.pos_concesionario',
    ['pos_journal_sequence.pos_journal_sequence',
        'web.rpc',
        'web.core',
        'point_of_sale.DB',
        'point_of_sale.screens',
        'point_of_sale.models',
        'web.Loading'],
    function(require) {
    'use strict';

    var core = require('web.core');
    var db = require('point_of_sale.DB');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var QWeb = core.qweb;
    var rpc = require('web.rpc')
    var Loading = require('web.Loading')
    var OrderSuper = models.Order;
    var PosModelSuper = models.PosModel;
    var _t = core._t;

    
    Loading.include({"on_rpc_event" : function(increment) {
        var self = this;
        console.log("asdas")
        if (!this.count && increment === 1) {
            // Block UI after 3s
            this.long_running_timer = setTimeout(function () {
                self.blocked_ui = true;
                framework.blockUI();
            }, 3000);
        }

        this.count += increment;
        if (this.count > 0) {
            if (session.debug) {
                this.$el.text(_.str.sprintf( _t("Loading123 (%d)"), this.count));
            } else {
                this.$el.text(_t("Loading123"));
            }
            this.$el.show();
            this.getParent().$el.addClass('oe_wait');
        } else {
            this.count = 0;
            clearTimeout(this.long_running_timer);
            // Don't unblock if blocked by somebody else
            if (self.blocked_ui) {
                this.blocked_ui = false;
                framework.unblockUI();
            }
            this.$el.fadeOut();
            this.getParent().$el.removeClass('oe_wait');
        }
    }})

    models.PosModel = models.PosModel.extend({
        init: function(parent, options) {
            var self = this;
            self.programacion_menu = []
            this._super(parent, options);
        },
    })    

    PosModelSuper.models.push({
        model: "ca.programacion",
        fields: ['empresa_id', 'product_ids', 'fecha'],
        domain: [
            ['fecha', '=', new Date()]
        ],
        loaded: function(self, programacion) {
            //self.db.add_products(products);
            var empresa = programacion.filter(
                function(p) {
                    return p["empresa_id"][0] == self.config.company_con_id[0]
                })
            if (empresa.length > 0) {
                self.programacion_menu = empresa[0].product_ids
            } else {
                self.programacion_menu = []
            }
        },
    })
    PosModelSuper.prototype.models[17].fields.push('es_menu')

    db.include({
        limit:300,
        get_all_partners_ids: function() {
            return this.all_partners_ids;
        },
        add_partners: function(partners, config) {

            var updated_count = 0;
            var new_write_date = '';
            var partners_filter = [];
            console.log("Add PArtners")
            console.log(config)
            if (config) {
                console.log(config)
                for (var i = 0, len = partners.length; i < len; i++) {
                    var partner = partners[i];
                    if (partner.empresa_id[0] == config.company_con_id[0]) {
                        if (partner.name && $.inArray(partner.id, this.all_partners_ids) == -1) {
                            this.partnerNameList.push(partner.vat + '|' + partner.name + '|' + partner.codigo);
                            this.all_partners_ids.push(partner.id);
                            partners_filter.push(partner);
                        }
                    }
                    var local_partner_date = (this.partner_write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                    var dist_partner_date = (partner.write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                    if (this.partner_write_date &&
                        this.partner_by_id[partner.id] &&
                        new Date(local_partner_date).getTime() + 1000 >=
                        new Date(dist_partner_date).getTime()) {
                        continue;
                    } else if (new_write_date < partner.write_date) {
                        new_write_date = partner.write_date;
                    }
                    if (!this.partner_by_id[partner.id]) {
                        this.partner_sorted.push(partner.id);
                    }
                    this.partner_by_id[partner.id] = partner;

                    updated_count += 1;
                }
                //console.log(this.partner_by_id)
                //this._super(partners_filter,config);
                this.partner_write_date = new_write_date || this.partner_write_date;
                if (updated_count) {
                    // If there were updates, we need to completely
                    // rebuild the search string and the barcode indexing

                    this.partner_search_string = "";
                    this.partner_by_barcode = {};

                    for (var id in this.partner_by_id) {
                        partner = this.partner_by_id[id];

                        if (partner.barcode) {
                            this.partner_by_barcode[partner.barcode] = partner;
                        }
                        partner.address = (partner.street || '') + ', ' +
                            (partner.zip || '') + ' ' +
                            (partner.city || '') + ', ' +
                            (partner.country_id[1] || '');
                        this.partner_search_string += this._partner_search_string(partner);
                    }
                }
            }

            updated_count += 1;


        },
    });

    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            var res = OrderSuper.prototype.initialize.apply(this, arguments);
            this.payment_id = false;
            return res;
        },
        set_payment_method: function(payment_id) {
            this.assert_editable();
            this.payment_id = payment_id;
        },
        get_payment_method: function() {
            return this.payment_id;
        },
    });

    screens.ClientListScreenWidget = screens.ClientListScreenWidget.extend({
        save_client_details: function(partner) {
            var self = this;
            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx, el) {
                fields[el.name] = el.value || false;
            });

            if (!fields.name) {
                this.gui.show_popup('error', _t('A Customer Name Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id = partner.id || false;
            fields.country_id = fields.country_id || false;
            fields.empresa_id = this.pos.config.company_con_id[0]
            fields.es_comensal = true
            fields.tipo = "externo"
            fields.tipo_documento = $('.tipo_doc_group:checked').val();
            console.log(fields)
            //new Model('res.partner').call('create_from_ui', [fields])
            rpc.query({
                model:"res.partner",
                method:"create_from_ui",
                args:[fields]
            })
            .then(function(partner_id) {
                self.saved_client_details(partner_id);
            }, function(err, event) {
                event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (err.data) {
                    var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error', {
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
            });
        },
        saved_client_details: function(partner_id) {
            var self = this;
            console.log("reload_partner")

            self.reload_partners().then(function() {
                console.log("Partner x")
                var partner = self.pos.db.get_partner_by_id(partner_id);
                console.log(partner)
                if (partner) {
                    self.new_client = partner;
                    self.toggle_save_button();
                    self.display_client_details('show', partner);
                } else {
                    // should never happen, because create_from_ui must return the id of the partner it
                    // has created, and reload_partner() must have loaded the newly created partner.
                    self.display_client_details('hide');
                }
            });
            setTimeout(function() {
                var partner = self.pos.db.get_partner_by_id(partner_id)
                self.pos.get_order().set_client(partner)
                console.log(partner)
                self.toggle_save_button();
                self.display_client_details('show', partner);
            }, 200)
        }
    })

    PosModelSuper.prototype.models[5].fields.push('empresa_id', 'es_comensal', 'es_empresa', 'codigo');
    PosModelSuper.prototype.models[5].loaded = function(self, partners) {
        self.partners = partners;
        console.log(partners)
        console.log(self)
        console.log(self.config)
        self.db.add_partners(partners, self.config);
    };

    
    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function() {
                var order = self.pos.get_order();

                if (!order.get_client()) {
                    self.gui.show_screen('products');
                    self.gui.show_popup('error', {
                        'title': _t('Una orden anónima no puede ser realizada'),
                        'body': _t('Debe seleccionar un  cliente antes de proceder con la venta'),
                    });

                    return false;
                }
                if (order.get_orderlines().length != 0) {
                    var has_valid_product_lot = _.every(order.orderlines.models, function(line) {
                        return line.has_valid_product_lot();
                    });

                    if (!has_valid_product_lot) {
                        self.gui.show_screen('products');
                        self.gui.show_popup('confirm', {
                            'title': _t('Empty Serial/Lot Number'),
                            'body': _t('One or more product(s) required serial/lot number.'),
                            confirm: function() {
                                self.validate_order();
                                order.finalize();
                            },
                        });
                    } else {
                        self.validate_order();
                        self.gui.show_screen('products');
                        order.finalize();
                        //self.print()
                    }
                } else {
                    self.gui.show_screen('products');
                    self.gui.show_popup('error', {
                        'title': _t('Empty Order'),
                        'body': _t('There must be at least one product in your order before it can be validated'),
                    });

                }


            });
        },
        order_is_valid: function(force_validation) {
            var self = this;
            var order = this.pos.get_order();

            // FIXME: this check is there because the backend is unable to
            // process empty orders. This is not the right place to fix it.
            if (order.get_orderlines().length === 0) {
                self.gui.show_screen('products');
                self.gui.show_popup('error', {
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before it can be validated'),
                });
                return false;
            }
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
                self.gui.show_screen('products');
                self.gui.show_popup('error', {
                    'title': _t('An anonymous order cannot be invoiced'),
                    'body': _t('You need to select the customer before you can invoice an order.'),
                });

                return false;
            }
            var plines = order.get_paymentlines();
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    self.gui.show_screen('products');
                    self.gui.show_popup('error', {
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return false;
                }
            }
            //VERIFICAR
            if (!order.is_paid() || this.invoicing) {
                self.gui.show_screen('products');
                self.gui.show_popup('error', {
                    title: _t('Amount not Paid'),
                    body: _t('Please choose a Payment Method to paid the order.'),
                });
                return false;
            }
            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(order.get_total_with_tax() - order.get_total_paid()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < this.pos.cashregisters.length; i++) {
                    cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    self.gui.show_screen('products');
                    self.gui.show_popup('error', {
                        title: _t('Cannot return change without a cash payment method'),
                        body: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return false;
                }
            }

            // if the change is too large, it's probably an input error, make the user confirm.
            if (!force_validation && order.get_total_with_tax() > 0 && (order.get_total_with_tax() * 1000 < order.get_total_paid())) {
                self.gui.show_screen('products');
                self.gui.show_popup('confirm', {
                    title: _t('Please Confirm Large Amount'),
                    body: _t('Are you sure that the customer wants to  pay') +
                        ' ' +
                        this.format_currency(order.get_total_paid()) +
                        ' ' +
                        _t('for an order of') +
                        ' ' +
                        this.format_currency(order.get_total_with_tax()) +
                        ' ' +
                        _t('? Clicking "Confirm" will validate the payment.'),
                    confirm: function() {
                        self.validate_order('confirm');
                    },
                });
                return false;
            }
            //Extraido de POS_JOURNAL_SEQUENCE
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
            return true;
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
        finalize_validation: function() {
            var self = this;
            var order = this.pos.get_order();
            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                this.pos.proxy.open_cashbox();
            }

            order.initialize_validation_date();
            order.finalized = true;

            if (order.is_to_invoice()) {
                var invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;

                invoiced.fail(function(error) {
                    self.invoicing = false;
                    order.finalized = false;
                    if (error.message === 'Missing Customer') {
                        self.gui.show_screen('products');
                        self.gui.show_popup('error', {
                            'title': _t('Please select the Customer'),
                            'body': _t('You need to select the customer before you can invoice an order.'),
                        });
                    } else if (error.code < 0) { // XmlHttpRequest Errors
                        self.gui.show_screen('products');
                        self.gui.show_popup('error', {
                            'title': _t('The order could not be sent'),
                            'body': _t('Check your internet connection and try again.'),
                        });
                    } else if (error.code === 200) { // OpenERP Server Errors
                        self.gui.show_screen('products');
                        self.gui.show_popup('error-traceback', {
                            'title': error.data.message || _t("Server Error"),
                            'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                        });
                    } else { // ???
                        self.gui.show_screen('products');
                        self.gui.show_popup('error', {
                            'title': _t("Unknown Error"),
                            'body': _t("The order could not be sent to the server due to an unknown error"),
                        });
                    }
                });

                invoiced.done(function() {
                    self.invoicing = false;
                    setTimeout(()=>{
                        self.gui.show_screen('receipt');
                    },2000)
                });
            } else {
                this.pos.push_order(order);
                setTimeout(()=>{
                    self.gui.show_screen('receipt');
                },2000)
            }

        },
        validate_order: function(force_validation) {
            self = this;
            if (this.validate_journal_invoice()) {
                return;
            }
            if (this.order_is_valid(force_validation)) {
                this.finalize_validation();
                return true;
            } else {
                return false;
            }

        },
    });

    screens.ProductListWidget.extend({
        
        render_product: function(product) {
            var cached = this.product_cache.get_node(product.id);
            if (!cached) {
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product', {
                    widget: this,
                    product: product,
                    image_url: this.get_product_image_url(product),
                });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id, product_node);
                return product_node;
            }
            return cached;
        },
        renderElement: function() {
            var el_str = QWeb.render(this.template, { widget: this });
            var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

            if (this.el && this.el.parentNode) {
                this.el.parentNode.replaceChild(el_node, this.el);
            }
            this.el = el_node;
            console.log(this.pos.programacion_menu)

            for (var i = 0, len = this.product_list.length; i < len; i++) {
                var product_node = this.render_product(this.product_list[i]);
                product_node.addEventListener('click', this.click_product_handler);
                if (this.pos.programacion_menu.indexOf(this.product_list[i].id) >= 0) {
                    el_node.querySelector('.product-list-menu').appendChild(product_node);
                } else if (!this.product_list[i].es_menu) {
                    el_node.querySelector('.product-list').appendChild(product_node);
                }

            }

        }
    });

    screens.PaymentScreenWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.paymentmethod_id = null;
            this.journal_id = null;

            var order = this.pos.get_order();
            this.paymentmethod_id = order.get_payment_method();
            this.journal_id = order.get_sale_journal();
            /*
            //Check Selected Journal
            if(this.paymentmethod_id){
                this.$('.paymentmethod').removeClass('highlight');
                this.$('div[data-id="'+this.paymentmethod_id+'"]').addClass('highlight');
            }

            if(this.journal_id){
                this.$('.js_sale_journal').removeClass('highlight');
                this.$('div[data-id="'+this.journal_id+'"]').addClass('highlight');
            }*/

            this.delete_paymentmethod(false);
            order.set_payment_method(false);
            this.$('.paymentmethod').removeClass('highlight');

        },
        click_paymentmethods: function(id) {
            var self = this;
            //this._super(id);
            var order = this.pos.get_order();
            var amount = order.get_total_with_tax();
            if (order.get_orderlines().length === 0) {
                this.gui.show_popup('error', {
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before it can be validated'),
                });
                return false;
            } else {
                if (order.get_payment_method() != id) {
                    order.set_payment_method(id);
                    this.$('.paymentmethod').removeClass('highlight');
                    this.$('div[data-id="' + id + '"]').addClass('highlight');
                    var paymentlines = this.pos.get_order().get_paymentlines();
                    //Remover otro método de pago
                    this.delete_paymentmethod(id);

                    //Agregar método de pago

                    var open_paymentline = false;



                    for (var i = 0; i < paymentlines.length; i++) {
                        if (!paymentlines[i].paid) {
                            open_paymentline = true;
                        }
                    }
                    //console.log(this.pos.cashregisters);

                    var id_cashier = null;
                    for (var i = 0; i < this.pos.cashregisters.length; i++) {
                        if (this.pos.cashregisters[i].journal_id[0] == id) {
                            id_cashier = i;
                        }
                    }

                    if (!open_paymentline) {
                        this.pos.get_order().add_paymentline(this.pos.cashregisters[id_cashier]);
                    }

                    if (order.selected_paymentline) {
                        order.selected_paymentline.set_amount(amount);
                        this.order_changes();
                        this.render_paymentlines();
                        this.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(amount));
                    }


                } else {
                    this.delete_paymentmethod(false);
                    order.set_payment_method(false);
                    this.$('.paymentmethod').removeClass('highlight');
                }
            }
        },
        delete_paymentmethod: function(id) {
            var paymentlines = this.pos.get_order().get_paymentlines();
            for (var i = 0; i < paymentlines.length; i++) {
                if (paymentlines[i].get_type() != id) {
                    this.pos.get_order().remove_paymentline(paymentlines[i]);
                    this.reset_input();
                    this.render_paymentlines();
                    return;
                }
            }
        }
    });

    screens.ProductScreenWidget.include({
        start: function() {

            this._super();
            this.payment_buttons = new screens.PaymentScreenWidget(this, {});
            this.payment_buttons.replace(this.$('.placeholder-PaymentButtons'));
            this.reload_partners();
            this.modification_screen();

            this.old_client = this.pos.get_order().get_client();
            this.new_client = false;
            this.partner_list = []
            this.partner_id_list = []
            this.partner_list = this.pos.db.get_all_partners_name();
            console.log(this.partner_list);
            this.partner_id_list = this.pos.db.get_all_partners_ids();
            var self = this;
            if (this.old_client) {
                this.$('.searchbox_2 input')[0].value = this.old_client.name;
            } else {
                this.$('.searchbox_2 input')[0].value = '';
                this.$('.searchbox_ input').focus();
            }
            $('.searchbox_2 input', this.el).keypress(function(e) {
                var keyCode = e.keyCode || e.which;
                if (keyCode != '13') {
                    $('.searchbox_2 input').autocomplete({
                        source: self.partner_list
                    });
                } else {
                    console.log(self.$('.searchbox_2 input').val())
                    self.search_client(self.$('.searchbox_2 input').val());
                    self.$('.searchbox_2 input').val("")
                }

            });

        },
        show: function() {
            var self = this;
            this._super();
            this.modification_screen();
        },
        modification_screen: function() {
            this.$('.categories').addClass('oe_hidden');
            this.$('.top-content').addClass('oe_hidden');
            this.$('.payment-numpad').addClass('oe_hidden');
            this.$('.paymentlines-container').addClass('oe_hidden');
            this.$('.left-content').removeClass('pc40');
            this.$('.right-content').removeClass('pc60');
            this.$('.js_set_customer').addClass('oe_hidden');
        },
        search_client: function(txtInput) {
            var self = this;
            var order = this.pos.get_order();
            var idx = -1;
            if (txtInput != '') {
                for (var i = 0; i < this.partner_list.length; i++) {
                    if (this.partner_list[i].toLowerCase().indexOf(txtInput.toLowerCase()) >= 0) {
                        idx = i;
                    }
                }
                if (idx == -1) {
                    this.gui.show_popup('error', {
                        'title': _t('Client not valid'),
                        'body': _t('Please check the name of the client. There\'s no client with that name.'),
                    });
                    this.$('.searchbox input').focus();
                    return false;
                } else {
                    var partner = this.pos.db.get_partner_by_id(this.partner_id_list[idx]);
                    this.new_client = partner;
                    var default_fiscal_position_id = _.find(this.pos.fiscal_positions, function(fp) {
                        return fp.id === self.pos.config.default_fiscal_position_id[0];
                    });
                    if (this.new_client && this.new_client.property_account_position_id) {
                        order.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                            return fp.id === self.new_client.property_account_position_id[0];
                        }) || default_fiscal_position_id;
                    } else {
                        order.fiscal_position = default_fiscal_position_id;
                    }
                    order.set_client(this.new_client);

                }
            } else {
                order.set_client(null);
            }


        },
        reload_partners: function() {
            var self = this;
            return this.pos.load_new_partners().then(function() {
                self.render_list(self.pos.db.get_partners_sorted(1000));
                console.log("set from product")
                    // update the currently assigned client if it has been changed in db.
                var curr_client = self.pos.get_order().get_client();
                if (curr_client) {
                    self.pos.get_order().set_client(self.pos.db.get_partner_by_id(curr_client.id));
                }
            });
        },
    });

});
