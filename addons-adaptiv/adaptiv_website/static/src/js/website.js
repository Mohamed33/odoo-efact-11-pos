odoo.define('adaptiv_website.website', function(require) {
"use strict";

var shell = require('adaptiv_web.shell');
var Shell = shell.Shell;
var ShellPane = shell.ShellPane;
var getShell = shell.getInstance;
var AppMenu = require('adaptiv_web.AppMenu');

var ajax = require('web.ajax');
var session = require('web.session');
var core = require('web.core');
var context = require('web_editor.context');
var base = require('web_editor.base');
var Widget = require('web.Widget');
var websiteNavbarData = require('website.navbar');
var qweb = core.qweb;

ajax.loadXML('/adaptiv_web/static/src/xml/shell.xml', qweb).then(function() {
  ajax.loadXML('/adaptiv_website/static/src/xml/app_menu.xml', qweb)
});

var WebsiteAppMenuLauncher = Widget.extend({
  start: function() {
    this.$el.on('click', function(ev) {
      ev.preventDefault();
      var shell = getShell();
      if(shell) {
        shell.getPane('app-menu').toggle();
      }
    });
  }
});

websiteNavbarData.websiteNavbarRegistry.add(WebsiteAppMenuLauncher, '.a_app_menu_toggler');

base.ready().then(function () {
  var shell = new Shell(undefined, $('#wrapwrap, #oe_main_menu_navbar'));
  shell.insertBefore($('#wrapwrap'));

  return session.rpc('/web/dataset/call_kw', {
      model: 'ir.ui.menu',
      method: 'load_menus',
      args: [false],
      kwargs: {
        context: context.get()
      }
  }).then(function(menu_tree) {
    var app_menu = new AppMenu(undefined, menu_tree, true);
    shell.addPane('app-menu', new ShellPane(
      app_menu, {
        side: 'left',
        template: 'ShellSidebarPane',
        displayLogo: true
      }
    ));
  });
});
});
