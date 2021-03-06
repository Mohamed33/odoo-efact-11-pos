odoo.define('pos_multi_uom.pos_multi_uom', function (require) {
"use strict";

var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');
var core = require('web.core');
var PosPopWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var _t = core._t;

models.load_fields('product.product',['has_multi_uom','multi_uom_ids']);

models.load_models([{
    model: 'product.multi.uom',
    condition: function(self){ return self.config.allow_multi_uom; },
    fields: ['multi_uom_id','price'],
    loaded: function(self,result){
        if(result.length){
            self.wv_uom_list = result;
        }
        else{
            self.wv_uom_list = [];
        }
    },
    }],{'after': 'product.product'});


    var MulitUOMWidget = PosPopWidget.extend({
        template: 'MulitUOMWidget',

        renderElement: function(){
            var self = this;
            this._super();
            this.$(".multi_uom_button").click(function(){
                var uom_id = $(this).data('uom_id');
                var price = $(this).data('price');
                var line = self.pos.get_order().get_selected_orderline();
                if(line){
                    line.set_unit_price(price);
                    line.set_product_uom(uom_id);
                }
                
                self.gui.show_screen('products');
            });
        },
        show: function(options){
            var self = this;
            this.options = options || {};
            var modifiers_list = [];
            var wv_uom_list = this.pos.wv_uom_list;
            var multi_uom_ids = options.product.multi_uom_ids;
            for(var i=0;i<wv_uom_list.length;i++){
                if(multi_uom_ids.indexOf(wv_uom_list[i].id)>=0){
                    modifiers_list.push(wv_uom_list[i]);
                }
            }
            options.wv_uom_list = modifiers_list;
            this._super(options); 
            this.renderElement();
        },
    });

    gui.define_popup({
        'name': 'multi-uom-widget', 
        'widget': MulitUOMWidget,
    });
    var ChangeUOMButton = screens.ActionButtonWidget.extend({
        template: 'ChangeUOMButton',
        button_click: function(){
            var self = this;
            var line = this.pos.get_order().get_selected_orderline();
            if(line){
                var product = line.get_product();
                if(product.multi_uom_ids.length > 0){
                    self.gui.show_popup('multi-uom-widget',{product:product});
                }
            }
        },
    });

    screens.define_action_button({
        'name': 'changeUOMbutton',
        'widget': ChangeUOMButton,
        'condition': function(){
            return this.pos.config.allow_multi_uom;
        },
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.wvproduct_uom = '';
        },
        set_product_uom: function(uom_id){
            this.wvproduct_uom = this.pos.units_by_id[uom_id];
            this.trigger('change',this);
        },

        get_unit: function(){
            var unit_id = this.product.uom_id;
            if(!unit_id){
                return undefined;
            }
            unit_id = unit_id[0];
            if(!this.pos){
                return undefined;
            }
            return this.wvproduct_uom == '' ? this.pos.units_by_id[unit_id] : this.wvproduct_uom;
        },

        export_as_JSON: function(){
            var unit_id = this.product.uom_id;
            var json = _super_orderline.export_as_JSON.call(this);
            json.product_uom = this.wvproduct_uom == '' ? unit_id.id : this.wvproduct_uom.id;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.wvproduct_uom = json.wvproduct_uom;
        },

    });

});

