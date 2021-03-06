odoo.define('adaptiv_web.AppMenu', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');

return Widget.extend({
  template: 'AppMenu',
  events: {
    'click a': function(evt) {
      var menu_id = $(evt.currentTarget).data('menu');
      if(!this.website && menu_id) {
        evt.preventDefault();
        this.trigger('menu_click', {
          menu_id: menu_id,
          action_id:  $(evt.currentTarget).data('action-id')
        });
      }
    }
  },

  init: function(parent, menu_tree, website){
    var self = this;
    this._super.apply(this, arguments);
    this.menu_tree = menu_tree;
    this.website = website;
  }
});
});
