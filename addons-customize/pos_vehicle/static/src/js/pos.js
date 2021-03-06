odoo.define('pos_vehicle.screens', function (require) {
    "use strict";
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var utils = require('web.utils');
    var session = require('web.session');
    var field_utils = require('web.field_utils');
    var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;
    var screens = require('point_of_sale.screens')
    var db = require('point_of_sale.DB')
    var QWeb = core.qweb;
    var _t = core._t;
    var ReceiptScreenWidget = require("pos_journal_sequence.pos_new_ticket").ReceiptScreenWidget
    var SeeAllOrdersScreenWidget = require("pos_orders_reprint.pos_orders_reprint").SeeAllOrdersScreenWidget

    models.load_models({
        model: 'res.vehicle',
        fields: ['id','placa', 'marca', 'modelo','anio_fabricacion',
                'km','fecha_ultimo_servicio','km_ultimo_servicio'],
        domain: function(self) {
            return [
            ];
        }, //['session_id', '=', self.pos_session.name],
        limit:40,
        loaded: function(self, vehicles) {
            self.db.vehicles = vehicles;
            self.db.get_vehicle_by_id = {};
            vehicles.forEach(function(vehicle) {
                self.db.get_vehicle_by_id[vehicle.id] = vehicle;
            });
            self.vehicles = vehicles;
        },
    });
    

    db.include({
        add_vehicles:function(vehicles){
            this.vehicle_search_string = "";
            for(var i = 0, len = vehicles.length; i < len; i++){
                var vehicle = vehicles[i]
                this.get_vehicle_by_id[vehicle.id] = vehicles[i];
                this.vehicle_search_string += this._vehicle_search_string(vehicle);
            }


            return vehicles.length
        },
        search_vehicle: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.vehicle_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_vehicle_by_id[id]);
                }else{
                    break;
                }
            }
            return results;
        },
        _vehicle_search_string: function(vehicle){
            var str =  vehicle.placa;
            str = '' + vehicle.id + ':' + str.replace(':','') + '\n';
            return str;
        }
    })

    var _super_pos = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize:function(session,attributes){
            var self = this;
            this.set({
                selectedVehicle:null
            })
            _super_pos.initialize.call(this, session, attributes);
            
            function update() {
                var order = self.get_order();
                this.set('selectedClient', order ? order.get_client() : null );
                this.set('selectedVehicle', order ? order.get_vehicle() : null );
            }
            this.get('orders').bind('add remove change', update, this);
            this.bind('change:selectedOrder', update, this);
    
        },
        get_vehicle:function(){
            return this.get_order().get_vehicle()
        },
        load_new_vehicles: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.models,function(model){ return model.model === 'res.vehicle'; }).fields;
            //var domain = [['write_date','>',this.db.get_partner_write_date()]];
            var domain = []
            rpc.query({
                    model: 'res.vehicle',
                    method: 'search_read',
                    args: [domain, fields],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function(vehicles){
                    if (self.db.add_vehicles(vehicles)) {   // check if the partners we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(type,err){ def.reject(); });
            return def;
        },
        
    })

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize:function(session,attributes){
            this.set({
                vehicle:false
            })
            var res = _super_order.initialize.call(this,session,attributes)
            return res;
        },
        export_as_JSON:function(){
            var orders = _super_order.export_as_JSON.call(this)
            var new_val = {}
            new_val = {
                vehicle:this.get_vehicle()
            }
            $.extend(orders,new_val)
            return orders
        },
        init_from_JSON:function(json){
            _super_order.init_from_JSON.call(this,json)
            this.set_vehicle(json.vehicle)
            this.set('vehicle',json.vehicle);
        },
        
        export_for_printing:function(){
            var orders = _super_order.export_for_printing.call(this);
            var new_val = {
                vehicle:this.get_vehicle()
            }
            $.extend(orders,new_val)
            return orders
        },
        get_vehicle:function(){
            return this.get('vehicle');
        },
        set_vehicle:function(vehicle){
            this.assert_editable();
            this.set('vehicle',vehicle);
        },
        get_vehicle_name: function(){
            var vehicle = this.get('vehicle');
            return vehicle ? vehicle.placa : "";
        },
    })

    var VechicleScreenEditWidget = PosBaseWidget.extend({
        init:function(parent,options){
            this._super(parent, options);
            this.renderElement()
        },
        renderElement:function(){
            this.$el = $(QWeb.render('VehicleDetails',{widget:this,vehicle:vehicle}))
        }
    })

    var VehicleScreenWidget = screens.ScreenWidget.extend({
        template:"VehicleScreenWidget",
        auto_back: true,
        
        show:function(options){
            var self = this;
            this._super(options)
            this.renderElement();
            this.details_visible = false;
            this.old_vehicle = this.pos.get_order().get_vehicle()

            this.$('.back').click(function(){
                self.gui.back();
            });
            this.$('.next').click(function(){   
                self.save_changes();
                self.gui.back();    // FIXME HUH ?
            });
            
            this.$('.new-vehicle').click(function(){
                self.display_vehicle_details('edit',{});
            });

            

            var vehicles = this.pos.vehicles;
            this.render_list(vehicles);
            this.reload_vehicles()

            if( this.old_vehicle ){
                this.display_vehicle_details('show',this.old_vehicle,0);
            }

            this.$('.vehicle-list-contents').delegate('.vehicles-line','click',function(event){
                self.line_select(event,$(this),parseInt($(this).data('id')));
            });
              
            var search_timeout = null;

            this.$('.searchbox input').on('keypress',function(event){
                clearTimeout(search_timeout);
                var searchbox = this;
                search_timeout = setTimeout(function(){
                    self.perform_search(searchbox.value, event.which === 13);
                },70);
            });
            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
            
            
        },
        hide: function () {
            this._super();
            this.new_vehicle = null;
        },
        perform_search: function(query, associate_result){
            var vehicles;
            if(query){
                vehicles = this.pos.db.search_vehicle(query);
                this.display_vehicle_details('hide');
                if ( associate_result && vehicles.length === 1){
                    this.new_vehicle = vehicles[0];
                    this.save_changes();
                    this.gui.back();
                }
                console.log(vehicles)
                this.render_list(vehicles);
            }else{
                var vehicles = this.pos.vehicles;
                this.render_list(vehicles);
            }
        },
        clear_search: function(){
            var vehicles = this.pos.db.vehicles;
            this.render_list(vehicles);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        render_list: function(vehicles){
            var contents = this.$el[0].querySelector('.vehicle-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(vehicles.length,1000); i < len; i++){
                //var vehicleline = this.pos.db.get_vehicle_by_id[vehicle.id];
                var vehicle = vehicles[i]
                var vehicleline_html = QWeb.render('VehicleLine',{widget: this, vehicle:vehicles[i]});
                var vehicleline = document.createElement('tbody');
                vehicleline.innerHTML = vehicleline_html;
                vehicleline = vehicleline.childNodes[1];
                    //this.partner_cache.cache_node(partner.id,clientline);
                if(this.old_vehicle){
                    if (this.old_vehicle.id == vehicle.id){
                        $(vehicleline).addClass('highlight');
                    }
                }else{
                    $(vehicleline).removeClass('highlight');
                }
                contents.appendChild(vehicleline);
            }
        },
        save_changes:function(){
            var order = this.pos.get_order();
            if(this.has_vehicle_changed()){
                order.set_vehicle(this.new_vehicle)
            }
        },
        has_vehicle_changed: function(){
            if( this.old_vehicle && this.new_vehicle ){
                return this.old_vehicle.id !== this.new_vehicle.id;
            }else{
                return !!this.old_vehicle !== !!this.new_vehicle;
            }
        },
        toggle_save_button:function(){
            var $button = this.$('.button.next');
            if (this.editing_vehicle) {
                $button.addClass('oe_hidden');
                return;
            } else if( this.new_vehicle ){
                if( !this.old_vehicle){
                    $button.text("Establecer vehículo");
                }else{
                    $button.text("Cambiar vehículo");
                }
            }else{
                $button.text("Remover vehículo");
            }
            $button.toggleClass('oe_hidden',!this.has_vehicle_changed());
        },
        line_select: function(event,$line,id){
            var vehicle = this.pos.db.get_vehicle_by_id[id];
            this.$('.vehicle-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.display_vehicle_details('hide',vehicle);
                this.new_vehicle = null;
                this.toggle_save_button();
            }else{
                this.$('.vehicle-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_vehicle_details('show',vehicle,y);
                this.new_vehicle = vehicle;
                this.toggle_save_button();
            }
        },
        display_vehicle_details:function(visibility,vehicle,clickpos){
            var self = this;
            var searchbox = this.$('.searchbox input');
            var contents = this.$('.vehicle-details-contents');
            var parent   = this.$('.vehicle-list').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();
            contents.off('click','.button.edit'); 
            contents.off('click','.button.save'); 
            contents.off('click','.button.undo'); 
            contents.on('click','.button.edit',function(){ self.edit_vehicle_details(vehicle); });
            contents.on('click','.button.save',function(){ self.save_vehicle_details(vehicle); });
            contents.on('click','.button.undo',function(){ self.undo_vehicle_details(vehicle); });
            
            

            this.editing_vehicle = false;
            this.uploaded_picture = null;
            

            if(visibility === 'show'){
                contents.empty();
                //this.$("#fecha_ultimo_servicio").datepicker();
                contents.append($(QWeb.render('VehicleDetailsEdit',{widget:this,vehicle:vehicle})));
                this.$el.find("#fecha_ultimo_servicio").datepicker()
                this.details_visible = true;
                this.toggle_save_button();
            } else if (visibility === 'edit') {
                // Connect the keyboard to the edited field
                if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                    contents.off('click', '.detail');
                    searchbox.off('click');
                    contents.on('click', '.detail', function(ev){
                        self.chrome.widget.keyboard.connect(ev.target);
                        self.chrome.widget.keyboard.show();
                    });
                    searchbox.on('click', function() {
                        self.chrome.widget.keyboard.connect($(this));
                    });
                }
    
                this.editing_vehicle = true;
                contents.empty();
                contents.append($(QWeb.render('VehicleDetailsEdit',{widget:this,vehicle:vehicle})));
                this.$el.find("#fecha_ultimo_servicio").datepicker()
                this.toggle_save_button();
    
                // Browsers attempt to scroll invisible input elements
                // into view (eg. when hidden behind keyboard). They don't
                // seem to take into account that some elements are not
                // scrollable.
                contents.find('input').blur(function() {
                    setTimeout(function() {
                        self.$('.window').scrollTop(0);
                    }, 0);
                });
    
            }else if (visibility === 'hide') {
                contents.empty();
                parent.height('100%');
                if( height > scroll ){
                    contents.css({height:height+'px'});
                    contents.animate({height:0},400,function(){
                        contents.css({height:''});
                    });
                }else{
                    parent.scrollTop( parent.scrollTop() - height);
                }
                this.details_visible = false;
                this.toggle_save_button();
            }
        },
        edit_vehicle_details:function(vehicle){
            this.display_vehicle_details('edit',vehicle);
        },
        save_vehicle_details:function(vehicle){
            var self = this;
            var fields = {};
            this.$('.vehicle-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });
            if (!fields.placa) {
                this.gui.show_popup('error',"El número de placa del vehículo es obligatorio");
                return;
            }
            
            fields.id = vehicle.id || false;

            var contents = this.$(".vehicle-details-contents");
            contents.off("click", ".button.save");
            
            rpc.query({
                    model: 'res.vehicle',
                    method: 'create_from_ui',
                    args: [fields],
                })
                .then(function(vehicle_id){
                    self.pos.db.get_vehicle_by_id[vehicle_id]  == fields
                    self.saved_vehicle_details(vehicle_id);
                },function(err,ev){
                    ev.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (err.data) {
                        var except = err.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Error: Could not Save Changes'),
                        'body': error_body,
                    });
                    contents.on('click','.button.save',function(){ self.save_vehicle_details(vehicle); });
                });
        },
        saved_vehicle_details: function(vehicle_id){
            var self = this;
            return this.reload_vehicles().then(function(){
                var vehicle = self.pos.db.get_vehicle_by_id[vehicle_id];
                if (vehicle) {
                    self.new_vehicle = vehicle;
                    self.toggle_save_button();
                    self.display_vehicle_details('show',vehicle);
                } else {
                    self.display_vehicle_details('hide');
                }
            })
            
            /*
            return this.reload_partners().then(function(){
                var partner = self.pos.db.get_partner_by_id(partner_id);
                if (partner) {
                    self.new_client = partner;
                    self.toggle_save_button();
                    self.display_client_details('show',partner);
                } else {
                    self.display_client_details('hide');
                }
            }).always(function(){
                $(".client-details-contents").on('click','.button.save',function(){ self.save_client_details(partner); });
            });
             */
        },
        undo_vehicle_details:function(vehicle){

        },
        
        
        
        
        reload_vehicles:function(){
            var self = this;
            return this.pos.load_new_vehicles().then(function(){
                self.render_list(self.pos.db.vehicles);
            })
        }
        
    })

    gui.define_screen({name:'vehicles', widget: VehicleScreenWidget});

    var VehicleControlButtonWidget = PosBaseWidget.extend({
        template:"VehicleControlButtonWidget",
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.pos.bind('change:selectedVehicle', function() {
                self.renderElement();
            });     
        },
        
        renderElement:function(){
            var self = this;
            this._super();
            this.$el.click(function(){
                self.gui.show_screen("vehicles")
            })
        }
    })

    var CustomerControlButtonsWidget = PosBaseWidget.extend({
        template:"CustomerControlButtonsWidget",
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
    
            this.pos.bind('change:selectedClient', function() {
                self.renderElement();
            });
        },
        renderElement:function(){
            var self = this;
            this._super();
            this.$el.click(function(){
                self.gui.show_screen('clientlist');
            });
        }
    })

    screens.ProductScreenWidget.include({
        start:function(){
            this._super();
            this.customercontrolbutton = new CustomerControlButtonsWidget(this,{});
            this.customercontrolbutton.replace(this.$('.placeholder-CustomerControlButtonsWidget'));
            this.vehiclecontrolbutton = new VehicleControlButtonWidget(this,{});
            this.vehiclecontrolbutton.replace(this.$('.placeholder-VehicleControlButtonWidget'));
        }
    })


    ReceiptScreenWidget = ReceiptScreenWidget.extend({
        get_receipt_render_env: function() {
            var res = this._super()
            var order = this.pos.get_order()
            res["vehicle"] = order.get_vehicle()
            return res
           
        }
    })

    SeeAllOrdersScreenWidget = SeeAllOrdersScreenWidget.extend({
        get_receipt_render_env_reprint:function(receipt){
            var res = this._super(receipt)
            res["vehicle"] = receipt["vehicle"]
            console.log(receipt)
            return res
        }
    })

    gui.define_screen({name: 'see_all_orders_screen_widget',widget: SeeAllOrdersScreenWidget});

    gui.define_screen({name:'receipt', widget: ReceiptScreenWidget});

    //gui.define_screen({name:'products', widget: screens.ProductScreenWidget});
})