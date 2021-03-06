odoo.define('adaptiv_web.settings', function(require) {
 "use strict";
  var BaseSettingRenderer = require('base.settings').Renderer;
  BaseSettingRenderer.include({
    // Prevent mobile rendering behaviour
    _activateSettingMobileTab: function (currentTab) {
      var tab = this.$(".tab[data-key='" + this.modules[this.currentIndex].key + "']");
      tab.addClass("selected");
    }
  })
});
