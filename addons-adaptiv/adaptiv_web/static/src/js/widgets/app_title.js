odoo.define('adaptiv_web.AppTitle', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');

return Widget.extend({
  template: 'AppTitle',
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
