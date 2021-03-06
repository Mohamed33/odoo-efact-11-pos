odoo.define('adaptiv_web.ControlPanel', function(require) {
    'use strict';

  var ControlPanel = require('web.ControlPanel');

  ControlPanel.include({
    update: function(status, options) {
      var self = this;
      _.forEach(this.nodes, function($node) {
        $node.removeClass('o_hidden');
      });
      this._super.apply(this, arguments);
      _.forEach(this.nodes, function($node) {
        if($node.children().length == 0) {
          $node.addClass('o_hidden');
        };
      });
    }
  });

});
