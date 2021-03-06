odoo.define('adaptiv_web.Loading', function(require) {
    'use strict';

  var Loading = require('web.Loading');
  var framework = require('web.framework');

  Loading.include({

    start: function() {
      this._super.apply(this, arguments);
      NProgress.configure({
        minimum: 0.1,
        showSpinner: false
      });
    },

    on_rpc_event: function(increment) {
      var self = this;
      if (!this.count && increment === 1) {
        // Block UI after 3s
        this.long_running_timer = setTimeout(function() {
          self.blocked_ui = true;
          framework.blockUI();
        }, 3000);
      }

      this.count += increment;
      if (this.count > 0) {
        if (this.count == 1) {
          NProgress.start();
        } else {
          NProgress.inc();
        }
        this.getParent().$el.addClass('oe_wait');
      } else {
        this.count = 0;
        clearTimeout(this.long_running_timer);
        // Don't unblock if blocked by somebody else
        if (self.blocked_ui) {
          this.blocked_ui = false;
          framework.unblockUI();
        }
        NProgress.done();
        this.getParent().$el.removeClass('oe_wait');
      }
    }
  });

});
