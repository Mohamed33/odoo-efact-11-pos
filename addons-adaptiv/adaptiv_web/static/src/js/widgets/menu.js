odoo.define('adaptiv_web.Menu', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');

return Widget.extend({
  template: 'Menu',
  events: {
    'click a': function(evt) {
      var menu_id = $(evt.currentTarget).data('menu');
      if(menu_id) {
        evt.preventDefault();
        this.trigger('menu_click', {
          menu_id: menu_id,
          action_id:  $(evt.currentTarget).data('action-id')
        });
      }
    }
  },

  init: function(parent, mobile) {
    this._super.apply(this, arguments);
    this.mobile = mobile;
    core.bus.on('change_primary_menu', this, this.change_menu);
  },

  change_menu: function(menu) {
    this.active_menu = menu;
    this.renderElement();
  }
});
});
