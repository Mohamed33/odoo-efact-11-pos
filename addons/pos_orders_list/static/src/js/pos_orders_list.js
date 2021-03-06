// pos_orders_list js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_orders_list.pos_orders_list', ['point_of_sale.models', 'point_of_sale.screens','web.session' ,'web.core', 'point_of_sale.gui', 'point_of_sale.popups', 'web.rpc', 'web.utils'], function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;


    var _t = core._t;


    // Load Models here...

    models.load_models({
        model: 'pos.order',
        fields: ['name', 'id', 'date_order', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'session_id', 'state', 'company_id', 'invoice_id'],
        domain: function(self) {
            return [
                ['state', 'not in', ['draft', 'cancel']]
            ];
        }, //['session_id', '=', self.pos_session.name],
        limit:40,
        loaded: function(self, orders) {
            self.db.all_orders_list = orders;
            self.db.get_orders_by_id = {};
            orders.forEach(function(order) {
                self.db.get_orders_by_id[order.id] = order;
            });

            self.orders = orders;
        },
    });
    
    models.load_models({
        model: 'pos.order.line',
        fields: ['order_id', 'product_id', 'discount', 'qty', 'price_unit'],
        domain: function(self) {
            var order_lines = []
            var orders = self.db.all_orders_list;
            for (var i = 0; i < orders.length; i++) {
                order_lines = order_lines.concat(orders[i]['lines']);
            }
            return [
                ['id', 'in', order_lines]
            ];
        },
        loaded: function(self, pos_order_line) {
            self.db.all_orders_line_list = pos_order_line;
            self.db.get_lines_by_id = {};
            pos_order_line.forEach(function(line) {
                self.db.get_lines_by_id[line.id] = line;
            });

            self.pos_order_line = pos_order_line;
        },
    });

    models.PosModel = models.PosModel.extend({
        load_server_data:function(){
            var self = this;
            var loaded = new $.Deferred();
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            function load_model(index){
                if(index >= self.models.length){
                    loaded.resolve();
                }else{
                    var model = self.models[index];
                    self.chrome.loading_message(_t('Loading')+' '+(model.label || model.model || ''), progress);

                    var cond = typeof model.condition === 'function'  ? model.condition(self,tmp) : true;
                    if (!cond) {
                        load_model(index+1);
                        return;
                    }

                    var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
                    var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
                    var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context || {};
                    var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
                    var order   = typeof model.order === 'function'   ? model.order(self,tmp):    model.order;
                    var limit = model.limit
                    progress += progress_step;
                    
                    if( model.model ){
                        var params = {
                            model: model.model,
                            context: _.extend(context, session.user_context || {}),
                        };

                        if (model.ids) {
                            params.method = 'read';
                            params.args = [ids, fields];
                        } else {
                            params.method = 'search_read';
                            params.domain = domain;
                            params.fields = fields;
                            params.orderBy = order;
                            if( limit){
                                params.limit = limit
                            }
                        }

                        rpc.query(params).then(function(result){
                            try{    // catching exceptions in model.loaded(...)
                                $.when(model.loaded(self,result,tmp))
                                    .then(function(){ load_model(index + 1); },
                                        function(err){ loaded.reject(err); });
                            }catch(err){
                                console.error(err.message, err.stack);
                                loaded.reject(err);
                            }
                        },function(err){
                            loaded.reject(err);
                        });
                    }else if( model.loaded ){
                        try{    // catching exceptions in model.loaded(...)
                            $.when(model.loaded(self,tmp))
                                .then(  function(){ load_model(index +1); },
                                        function(err){ loaded.reject(err); });
                        }catch(err){
                            loaded.reject(err);
                        }
                    }else{
                        load_model(index + 1);
                    }
                }
            }

            try{
                load_model(0);
            }catch(err){
                loaded.reject(err);
            }

            return loaded;
        }
    })

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        _save_to_server: function(orders, options) {
            var self = this;
            return _super_posmodel._save_to_server.call(this, orders, options).then(function(new_orders) {
                if (new_orders != null) {
                    new_orders.forEach(function(order) {
                        if (order) {

                            //new Model('pos.order').call('return_new_order', [order])
                            rpc.query({
                                model: 'pos.order',
                                method: 'return_new_order',
                                args: [order]
                            }).then(function(output) {
                                self.db.all_orders_list.unshift(output);
                                self.db.get_orders_by_id[order.id] = order;
                            });


                            //######################################################################################

                            rpc.query({
                                model: 'pos.order',
                                method: 'return_new_order_line',
                                args: [order],

                            }).then(function(output1) {
                                for (var ln = 0; ln < output1.length; ln++) {
                                    self.db.all_orders_line_list.unshift(output1[ln]);
                                }
                                //self.db.all_orders_list.unshift(output);
                                //self.db.get_orders_by_id[order.id] = order;
                            });

                            //######################################################################################



                            //self.db.get_orders_by_id[order.id] = order;
                            // self.db.all_orders_list.unshift(orders[0]['data']);
                            //self.db.get_orders_by_id[order.id] = order;
                        }
                    });
                }
                return new_orders;
            });
        }

    });


    // SeeAllOrdersScreenWidget start

    var SeeAllOrdersScreenWidget = screens.ScreenWidget.extend({
        template: 'SeeAllOrdersScreenWidget',
        init: function(parent, options) {
            this._super(parent, options);
            //this.options = {};
            this.time_last = 0
        },

        line_selects: function(event, $line, id) {
            var self = this;
            var orders = this.pos.db.get_orders_by_id[id];
            this.$('.client-list .lowlight').removeClass('lowlight');
            if ($line.hasClass('highlight')) {
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                //this.display_orders_detail('hide',orders);
                //this.new_clients = null;
                //this.toggle_save_button();
            } else {
                this.$('.client-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_orders_detail('show', orders, y);
                //this.new_clients = orders;
                //this.toggle_save_button();
            }

        },

        display_orders_detail: function(visibility, order, clickpos) {
            var self = this;
            var contents = this.$('.client-details-contents');
            var parent = this.$('.orders-line ').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();

            //contents.off('click', '.button.edit');
            contents.off('click', '.button.save');
            contents.off('click', '.button.undo');

            contents.on('click', '.button.save', function() { self.save_client_details(order); });
            contents.on('click', '.button.undo', function() { self.undo_client_details(order); });


            this.editing_client = false;
            this.uploaded_picture = null;

            if (visibility === 'show') {
                contents.empty();


                //Custom Code for passing the orderlines
                var orderline = [];
                for (var z = 0; z < order.lines.length; z++) {
                    orderline.push(self.pos.db.get_lines_by_id[order.lines[z]])
                }
                //Custom code ends

                contents.append($(QWeb.render('OrderDetails', { widget: this, order: order, orderline: orderline })));

                var new_height = contents.height();

                if (!this.details_visible) {
                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
                //this.toggle_save_button();
            } else if (visibility === 'edit') {
                // Connect the keyboard to the edited field
                if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                    contents.off('click', '.detail');
                    searchbox.off('click');
                    contents.on('click', '.detail', function(ev) {
                        self.chrome.widget.keyboard.connect(ev.target);
                        self.chrome.widget.keyboard.show();
                    });
                    searchbox.on('click', function() {
                        self.chrome.widget.keyboard.connect($(this));
                    });
                }

                this.editing_client = true;
                contents.empty();
                contents.append($(QWeb.render('ClientDetailsEdit', { widget: this })));
                //this.toggle_save_button();

                // Browsers attempt to scroll invisible input elements
                // into view (eg. when hidden behind keyboard). They don't
                // seem to take into account that some elements are not
                // scrollable.
                contents.find('input').blur(function() {
                    setTimeout(function() {
                        self.$('.window').scrollTop(0);
                    }, 0);
                });

                contents.find('.image-uploader').on('change', function(event) {
                    self.load_image_file(event.target.files[0], function(res) {
                        if (res) {
                            contents.find('.client-picture img, .client-picture .fa').remove();
                            contents.find('.client-picture').append("<img src='" + res + "'>");
                            contents.find('.detail.picture').remove();
                            self.uploaded_picture = res;
                        }
                    });
                });
            } else if (visibility === 'hide') {
                contents.empty();
                if (height > scroll) {
                    contents.css({ height: height + 'px' });
                    contents.animate({ height: 0 }, 400, function() {
                        contents.css({ height: '' });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
                //this.toggle_save_button();
            }
        },

        get_selected_partner: function() {
            var self = this;
            if (self.gui)
                return self.gui.get_current_screen_param('selected_partner_id');
            else
                return undefined;
        },

        render_list_orders: function(orders, search_input) {
            var self = this;
            var selected_partner_id = this.get_selected_partner();
            var selected_client_orders = [];
            if (selected_partner_id != undefined) {
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id[0] == selected_partner_id)
                        selected_client_orders = selected_client_orders.concat(orders[i]);
                }
                orders = selected_client_orders;
            }

            if (search_input != undefined && search_input != '') {
                var selected_search_orders = [];
                var search_text = search_input.toLowerCase()
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id == '') {
                        orders[i].partner_id = [0, '-'];
                    }
                    if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                        selected_search_orders = selected_search_orders.concat(orders[i]);
                    }
                }
                orders = selected_search_orders;
            }


            var content = this.$el[0].querySelector('.orders-list-contents');
            content.innerHTML = "";
            var orders = orders;
            for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                var order = orders[i];
                var ordersline_html = QWeb.render('OrdersLine', { widget: this, order: orders[i], selected_partner_id: orders[i].partner_id[0] });
                var ordersline = document.createElement('tbody');
                ordersline.innerHTML = ordersline_html;
                ordersline = ordersline.childNodes[1];
                content.appendChild(ordersline);

            }
        },

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

            //new Model('res.partner').call('create_from_ui',[fields])
            rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [fields],

            }).then(function(partner_id) {
                self.saved_client_details(partner_id);
            }, function(err, event) {
                event.preventDefault();
                self.gui.show_popup('error', {
                    'title': _t('Error: Could not Save Changes'),
                    'body': _t('Your Internet connection is probably down.'),
                });
            });
        },

        undo_client_details: function(partner) {
            this.display_orders_detail('hide');

        },

        saved_client_details: function(partner_id) {
            var self = this;
            self.display_orders_detail('hide');
            alert('!! Customer Created Successfully !!')

        },
        click_line:function(id){
            var self = this;
            var orders1 = self.pos.db.all_orders_list;
            var orders_lines = self.pos.db.all_orders_line_list;
            for (var ord = 0; ord < orders1.length; ord++) {
                if (orders1[ord]['id'] == id) {
                    var orders1 = orders1[ord];
                }
            }
            var orderline = []
            for (var n = 0; n < orders_lines.length; n++) {
                if (orders_lines[n]['order_id'][0] == id) {
                    orderline.push(orders_lines[n])
                }
            }
            console.log(orderline)
            //Custom Code for passing the orderlines
            orders1["date_order"] = moment(new Date(moment(orders1["date_order"],"YYYY-MM-DD HH:mm:ss").toDate().getTime()-5*60*60*1000)).format("YYYY-MM-DD HH:mm:ss")
            self.gui.show_popup('see_order_details_popup_widget', { 'order': [orders1], 'orderline': orderline });
        },
        show: function(options) {
            var self = this;
            this._super(options);

            this.details_visible = false;

            //var orders = self.pos.db.all_orders_list;
            //var orders_lines = self.pos.db.all_orders_line_list;
            
            rpc.query({
                model: 'pos.order',
                method: 'search_read',
                args: [],
                context: session.user_context,
                kwargs: {
                    limit: 20,
                    offset: 0,
                    domain:[["config_id","=",self.pos.config.id]]
                }
            })  
            .then(function(orders) {
                var content = self.$el[0].querySelector('.orders-list-contents');
                content.innerHTML = "";

                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    var order = orders[i];
                    order["date_order"] = moment(new Date(moment(order["date_order"],"YYYY-MM-DD HH:mm:ss").toDate().getTime()-5*60*60*1000)).format("YYYY-MM-DD HH:mm:ss")
                    var ordersline_html = QWeb.render('OrdersLine', { widget: self, order: order, selected_partner_id: order.partner_id[0] });
                    var ordersline = document.createElement('tbody');
                    ordersline.innerHTML = ordersline_html;
                    ordersline = ordersline.childNodes[1];
                    content.appendChild(ordersline);
                }
            })

            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-name', 'click', function(event) {
                var id = $(this).data('id')
                self.click_line(id)
            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-ref', 'click', function(event) {
                var id = $(this).data('id')
                self.click_line(id)
            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-partner', 'click', function(event) {
                var id = $(this).data('id')
                self.click_line(id)
            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-date', 'click', function(event) {
                var id = $(this).data('id')
                self.click_line(id)
            });

            //################################################################################################################

            //################################################################################################################
            this.$('.orders-list-contents').delegate('.orders-line-tot', 'click', function(event) {
                var id = $(this).data('id')
                self.click_line(id)
            });

            //################################################################################################################


            //this code is for click on order line & that order will be appear 

            //this.$('.orders-list-contents').delegate('.orders-line', 'click', function(event) {

            //var orders1 = self.pos.db.get_orders_by_id[parseInt($(this).data('id'))];

            //Custom Code for passing the orderlines
            //var orderline = [];
            //for (var z = 0; z < orders1.lines.length; z++){
            //orderline.push(self.pos.db.get_lines_by_id[orders1.lines[z]])
            //}
            //Custom code ends

            //console.log('tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt',orders1, orderline);
            //self.gui.show_popup('see_order_details_popup_widget', {'order': [orders1], 'orderline':orderline});
            //self.line_selects(event, $(this), parseInt($(this).data('id')));
            //});

            //this code is for Search Orders
            this.$('.search-order input').keyup(function() {
                self.time_last = Date.now();
                var val = this.value
                setTimeout(function() {
                    console.log(Date.now() - self.time_last)
                    if (Date.now() - self.time_last >= 1000) {
                        
                        rpc.query({
                            model: 'pos.order',
                            method: 'search_read',
                            args: [],
                            kwargs: {
                                domain: ['&','|', '|', '|',["config_id","=",self.pos.config.id], ["pos_reference", "ilike", val],
                                    ["partner_id.name", "ilike", val],
                                    ["number", "ilike", val],
                                    ["date_order", "ilike", val],
                                    ['state', 'not in', ['draft', 'cancel']]
                                ],
                                limit: 20,
                                offset: 0,
                                fields: ['name', 'id', 'date_order', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'session_id', 'state', 'company_id', 'invoice_id'],
                            }
                        }).then(function(orders) {
                            self.pos.db.all_orders_list = self.pos.db.all_orders_list.concat(orders)
                            var order_lines_1 =[]
                            orders.forEach(function(order) {
                                self.pos.db.get_orders_by_id[order.id] = order;
                                order_lines_1 = order_lines_1.concat(order["lines"])
                            });
                            rpc.query({
                                model:"pos.order.line",
                                method:"search_read",
                                args:[],
                                kwargs: {
                                    domain: [["id","in",order_lines_1]],
                                    offset:0,
                                    fields:['order_id', 'product_id', 'discount', 'qty', 'price_unit']
                                }
                            }).then(function(lines){
                                self.pos.db.all_orders_line_list = self.pos.db.all_orders_line_list.concat(lines);
                                self.pos.db.get_lines_by_id = {};
                                lines.forEach(function(line) {
                                    self.pos.db.get_lines_by_id[line.id] = line;
                                });
                                self.pos_order_line = lines;

                                var content = self.$el[0].querySelector('.orders-list-contents');
                                content.innerHTML = "";
                                    
                                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                                    var order = orders[i];
                                    order["date_order"] = moment(new Date(moment(order["date_order"],"YYYY-MM-DD HH:mm:ss").toDate().getTime()-5*60*60*1000)).format("YYYY-MM-DD HH:mm:ss")
                                    var ordersline_html = QWeb.render('OrdersLine', { widget: self, order: order, selected_partner_id: order.partner_id[0] });
                                    var ordersline = document.createElement('tbody');
                                    ordersline.innerHTML = ordersline_html;
                                    ordersline = ordersline.childNodes[1];
                                    content.appendChild(ordersline);
                                    
                                }
                                self.time_last = Date.now()
                            })
                            

                            


                        })
                    }
                }, 1001);
            });

            this.$('.new-customer').click(function() {
                self.display_orders_detail('edit', {
                    'country_id': self.pos.company.country_id,
                });
            });



        },

    });

    gui.define_screen({
        name: 'see_all_orders_screen_widget',
        widget: SeeAllOrdersScreenWidget
    });

    var SeeOrderDetailsPopupWidget = popups.extend({
        template: 'SeeOrderDetailsPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        show: function(options) {
            var self = this;
            options = options || {};
            this._super(options);
            this.order = options.order || [];
            this.orderline = options.orderline || [];
        },
        events: {
            'click .button.cancel': 'click_cancel',
        },
        renderElement: function() {
            this._super();
        },

    });



    gui.define_popup({
        name: 'see_order_details_popup_widget',
        widget: SeeOrderDetailsPopupWidget
    });


    // Start SeeAllOrdersButtonWidget

    var SeeAllOrdersButtonWidget = screens.ActionButtonWidget.extend({
        template: 'SeeAllOrdersButtonWidget',

        button_click: function() {
            var self = this;
            this.gui.show_screen('see_all_orders_screen_widget', {});
        },

    });

    screens.define_action_button({
        'name': 'See All Orders Button Widget',
        'widget': SeeAllOrdersButtonWidget,
        'condition': function() {
            return true;
        },
    });
    // End SeeAllOrdersButtonWidget	

    // Start ClientListScreenWidget
    gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist' })[0].widget.include({
        show: function() {
            this._super();
            var self = this;
            this.$('.view-orders').click(function() {
                self.gui.show_screen('see_all_orders_screen_widget', {});
            });


            $('.selected-client-orders').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget', {
                    'selected_partner_id': this.id
                });
            });

        },
    });

    return {
        SeeAllOrdersScreenWidget:SeeAllOrdersScreenWidget
    };
});