odoo.define('adaptiv_web.debrand', function (require) {
"use strict";

var WebClient = require('web.WebClient');
var TranslationDataBase = require('web.translation').TranslationDataBase;
var title = document.title;


WebClient.include({
  init: function (parent) {
    this._super(parent);
    this.set('title_part', {"zopenerp": title});
  },
});

TranslationDataBase.include({
  get: function(key) {
    var res = this._super(key);
    var res = res == null ? key : res;
    if (res != null) {
      res.replace('odoo', title);
      res.replace('Odoo', title);
    }
    return res;
  }
});

});
