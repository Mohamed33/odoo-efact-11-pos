odoo.define('pos_product_switch_view.screens', function (require) {
"use strict";

var module = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;
var models = module.PosModel.prototype.models;

screens.ProductCategoriesWidget.include({
    renderElement: function(){
        var self = this;
        this._super();
        self.pos.listview = false;
        
        var node_el = self.el.querySelector('.breadcrumbs').childNodes[1];

        var span_el_lst = document.createElement('span');
        span_el_lst.classList.add('breadcrumb-button');
        span_el_lst.classList.add('breadcrumb-home');
        span_el_lst.classList.add('js-list-switch');
        
        var i_el_lst = document.createElement('i');
        i_el_lst.classList.add('fa');
        i_el_lst.classList.add('fa-list-alt');
        span_el_lst.appendChild(i_el_lst);
        
        var span_el_form = document.createElement('span');
        span_el_form.classList.add('breadcrumb-button');
        span_el_form.classList.add('breadcrumb-home');
        span_el_form.classList.add('js-form-switch');
        
        var i_el_form = document.createElement('i');
        i_el_form.classList.add('fa');
        i_el_form.classList.add('fa-th');
        span_el_form.appendChild(i_el_form);
        
        node_el.appendChild(span_el_lst);
        node_el.appendChild(span_el_form);
        
        $('.js-list-switch').click(function(){
            self.pos.listview = true;
            self.pos.config.pos_product_view = 'product_list_view';
            self.renderElement();
        });
        $('.js-form-switch').click(function(){
            self.pos.listview = true;
            self.pos.config.pos_product_view = 'product_form_view';
            self.renderElement();
        });
    },
});

screens.ProductListWidget.include({
    render_product: function(product){
        var self = this;
        var current_pricelist = this._get_active_pricelist();
        var cached = this.product_cache.get_node(product.id);
        if(!cached || this.pos.listview || this.pos.config.pos_product_view){
            if (this.pos.config.pos_product_view == 'product_list_view'){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{
                        widget:  this,
                        product: product,
                        pricelist: current_pricelist,
                        image_url: this.get_product_image_url(product),
                    });
                var product_node = document.createElement('tbody');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id,product_node);
                return product_node;
            }
            if (this.pos.config.pos_product_view == 'product_form_view'){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{
                        widget:  this,
                        product: product,
                        image_url: this.get_product_image_url(product),
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id,product_node);
                return product_node;
            }
        }
        return cached;
    },
    renderElement: function() {
        var el_str  = QWeb.render(this.template, {widget: this});
        var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

        if(this.el && this.el.parentNode){
            this.el.parentNode.replaceChild(el_node,this.el);
        }
        this.el = el_node;

        var list_container = el_node.querySelector('.product-list');
        for(var i = 0, len = this.product_list.length; i < len; i++){
            var product_node = this.render_product(this.product_list[i]);
            product_node.addEventListener('click',this.click_product_handler);
            list_container.appendChild(product_node);
        }
    },
    calculate_cache_key: function(product, pricelist){
        return product + ',' + pricelist;
    },
    _get_active_pricelist: function(){
        var current_order = this.pos.get_order();
        var current_pricelist = this.pos.default_pricelist;

        if (current_order) {
            current_pricelist = current_order.pricelist;
        }

        return current_pricelist;
    },
});
});
