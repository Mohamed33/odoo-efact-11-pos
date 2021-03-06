odoo.define('adaptiv_web.CalendarRenderer', function(require) {
    'use strict';

    var CalendarRenderer = require('web.CalendarRenderer');

    CalendarRenderer.include({
      getColor: function (key) {
          if (!key) {
              return;
          }
          if (this.color_map[key]) {
              return this.color_map[key];
          }
          // check if the key is a css color
          if (typeof key === 'string' && key.match(/^((#[A-F0-9]{3})|(#[A-F0-9]{6})|((hsl|rgb)a?\(\s*(?:(\s*\d{1,3}%?\s*),?){3}(\s*,[0-9.]{1,4})?\))|)$/i)) {
              return this.color_map[key] = key;
          }
          // CHANGE to 19 colors, can't visually distinct more
          var index = (((_.keys(this.color_map).length + 1) * 5) % 19) + 1;
          this.color_map[key] = index;
          return index;
      },
    });
  });
