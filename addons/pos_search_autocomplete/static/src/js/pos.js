odoo.define('pos_search_autocomplete.pos', ['point_of_sale.screens', 'point_of_sale.DB'], function(require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var db = require('point_of_sale.DB');

    db.include({
        init: function(options) {
            this._super(options);
            this.productNameList = [];
            this.partnerNameList = [];
            this.all_partners_ids = [];
        },
        add_products: function(products) {
            for (var i = 0, len = products.length; i < len; i++) {
                var product = products[i];
                if (product.display_name) {
                    this.productNameList.push(product.display_name);
                }
            }
            this._super(products);
        },
        get_all_products_name: function() {
            return this.productNameList;
        },
        add_partners: function(partners) {
            for (var i = 0, len = partners.length; i < len; i++) {
                var partner = partners[i];
                if (partner.name && $.inArray(partner.id, this.all_partners_ids) == -1) {
                    this.partnerNameList.push(partner.name);
                    this.all_partners_ids.push(partner.id);
                }
            }
            this._super(partners);
        },
        get_all_partners_name: function() {
            return this.partnerNameList;
        },
    });

    screens.ProductCategoriesWidget.include({
        renderElement: function() {
            this._super();
            var prod_list = this.pos.db.get_all_products_name();
            this.el.querySelector('.searchbox input').addEventListener('keyup', this.search_handler);
            $('body.ui-autocomplete').css('font-size', '200px');

            $('.searchbox input', this.el).keypress(function(e) {
                /*
                $('.searchbox input').autocomplete({
                    source: prod_list
                });*/
                $('.searchbox input').autocomplete({
                    source: function(request, response) {
                        var word = request.term
                        var keywords = word.split(" ")
                        var prod_list_temp = prod_list;
                        keywords.forEach(function(w) {
                            prod_list_temp = _.filter(prod_list_temp, function(e) {
                                return e.toUpperCase().indexOf(w.toUpperCase()) >= 0
                            })
                        });
                        response(prod_list_temp)
                    }
                });
                e.stopPropagation();
            });
        },
        clear_search: function() {
            this._super();
            $('span.ui-helper-hidden-accessible').html("");
            $('ul.ui-autocomplete').css('display', 'none');
        },
    });

    screens.ClientListScreenWidget.include({
        show: function() {
            this._super();
            var partner_list = []
            partner_list = this.pos.db.get_all_partners_name();
            $('.searchbox input', this.el).keypress(function(e) {

                $('.searchbox input').autocomplete({
                    source: partner_list
                });

            });
        },
        clear_search: function() {
            this._super();
            $('span.ui-helper-hidden-accessible').html("");
            $('ul.ui-autocomplete').css('display', 'none');
        },
    });
});