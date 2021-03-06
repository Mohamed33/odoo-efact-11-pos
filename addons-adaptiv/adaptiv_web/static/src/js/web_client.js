odoo.define('web.WebClient', function (require) {
  "use strict";

  var shell = require('adaptiv_web.shell');
  var Shell = shell.Shell;
  var ShellPane = shell.ShellPane;

  var AbstractWebClient = require('web.AbstractWebClient');
  var core = require('web.core');
  var data = require('web.data');
  var data_manager = require('web.data_manager');
  var session = require('web.session');
  var SystrayMenu = require('web.SystrayMenu');
  var UserMenu = require('web.UserMenu');
  var Menu = require('adaptiv_web.Menu');
  var AppMenu = require('adaptiv_web.AppMenu');
  var AppTitle = require('adaptiv_web.AppTitle');

  return AbstractWebClient.extend({

    ready: false,

    events: _.extend({}, AbstractWebClient.prototype.events, {
      'click .a_app_menu_toggler': function (ev) {
        ev.preventDefault();
        this.toggle_app_menu();
      },
      'click .a_menu_toggler': function (ev) {
        ev.preventDefault();
        this.toggle_menu();
      }
    }),

    show_application: function () {
      var self = this;

      // Allow to call `on_attach_callback` and `on_detach_callback` when needed
      this.action_manager.is_in_DOM = true;

      this.set_title();
      this.set_shell();

      var lazyreflow = _.debounce(this.reflow.bind(this), 100);
      return this.load_menu_tree().then(function (menu_tree) {
        // Keep for further use
        self.menu_tree = menu_tree;
        return self.create_widgets().then(function () {
          core.bus.on('resize', self, function () {
            lazyreflow();
          });

          $(window).bind('hashchange', self.on_hashchange);
        }).then(function () {
          var state = $.bbq.getState(true);
          if (_.isEmpty(state) || state.action === 'login') {
            // Upon opening a new web client without hash, we
            // see if there is a home action present
            return self._rpc({
              model: 'res.users',
              method: 'read',
              args: [[session.uid], ['action_id']]
            }).then(function (data) {
              if (data[0].action_id) {
                var menu = self.find_menu_by_action(data[0].action_id[0]);
                if (menu) {
                  self.do_menu_id(menu.id);
                }
                return self.do_menu_action(data[0].action_id[0]).then(function () {
                  return data[0].action_id;
                });
              }
            });
          }
        }).then(function (home_action_id) {
          if (home_action_id === undefined) {
            // Make sure primary menu's are rendered
            $(window).trigger('hashchange');
          }
          self.ready = true;
        });
      });
    },

    start: function () {
      var self = this;
      this.$menu_placeholder = this.$el.find('.a_menu_placeholder');
      return this._super.apply(this, arguments);
    },

    set_shell: function () {
      this.shell = new Shell(this, this.$('.a_canvas'));
      return this.shell.prependTo(this.$el);
    },

    load_menu_tree: function () {
      return this._rpc({
        model: 'ir.ui.menu',
        method: 'load_menus',
        args: [core.debug],
        context: session.user_context
      }).then(function (menu_tree) {
        return menu_tree
      });
    },

    // --------------------------------------------------------------------------
    // Layout
    // --------------------------------------------------------------------------
    is_mobile: function () {
      return (window.getComputedStyle
        && (window.getComputedStyle(this.$el.get()[0], ':after')
          .getPropertyValue('content').replace(/"/g, '') === 'mobile')
        || false);
    },

    reflow: function () {
      var self = this;
      var mobile = this.is_mobile();
      if (mobile !== this._widgets_mobile) {
        // Switched from mobile to desktop mode or visa versa
        return this.create_widgets().then(function () {
          // Make sure primary menu's are (re)rendered
          core.bus.trigger('change_primary_menu', self._primary_menu);
        })
      }
    },

    create_widgets: function () {
      var defs = [];
      var mobile = this.is_mobile();

      // Destroy previously created panes
      if (this.shell.getPane('app-menu')) {
        this.shell.getPane('app-menu').destroy();
      }

      if (this.shell.getPane('menu')) {
        this.shell.getPane('menu').destroy();
      }

      // App menu
      if (this.app_menu) {
        this.app_menu.destroy();
      }
      this.app_menu = new AppMenu(this, this.menu_tree);
      this.app_menu.on('menu_click', this, this.on_app_menu_click);
      this.shell.addPane('app-menu', new ShellPane(
        this.app_menu, {
          side: 'left',
          template: 'ShellSidebarPane',
          displayLogo: true,
          company: session.company_id
        }
      ));

      // Primary nav menu
      if (this.menu) {
        this.menu.destroy();
      }
      this.menu = new Menu(this, mobile);
      this.menu.on('menu_click', this, this.on_menu_click);
      if (!mobile) {
        defs.push(this.menu.appendTo(this.$menu_placeholder));
      }

      // App  title
      if (this.app_title) {
        this.app_title.destroy();
      }
      this.app_title = new AppTitle(this, mobile);
      defs.push(this.app_title.insertAfter(this.$el.find('.a_app_menu_toggler')));

      // Systray
      if (this.systray_menu) {
        this.systray_menu.destroy();
      }
      this.systray_menu = new SystrayMenu(this);
      defs.push(this.systray_menu.appendTo(this.$menu_placeholder));

      // User menu
      if (this.user_menu) {
        this.user_menu.destroy();
      }
      this.user_menu = new UserMenu(this);
      defs.push(this.user_menu.appendTo(this.$menu_placeholder));

      if (mobile) {
        this.shell.addPane('menu', new ShellPane(
          this.menu, {
            side: 'right',
            template: 'ShellSidebarPane'
          }
        ));
      }

      this._widgets_mobile = mobile;
      return $.when.apply($, defs);
    },

    // --------------------------------------------------------------------------
    // Helper functions to find and navigate the menu_tree
    // --------------------------------------------------------------------------
    find_menu: function (predicate, primary, menu) {
      var self = this;
      menu = menu || this.menu_tree;
      if (predicate(menu)) {
        return menu;
      }

      var result = null;
      _.find(menu.children, function (child) {
        var found = self.find_menu(predicate, false, child);
        if (found) {
          result = primary ? child : found;
          return true;
        }
      });

      return result;
    },

    find_nearest_action: function (menu_id) {
      var parent_menu_id;
      return this.find_menu(function (menu) {
        if (menu.id === menu_id || menu.parent_id && menu.parent_id[0] === parent_menu_id) {
          parent_menu_id = menu.id;
          if (menu.action) {
            return true;
          }
        }
      }).action.split(',')[1];
    },

    find_menu_by_action: function (action_id) {
      return this.find_menu(function (menu) {
        return menu.action && menu.action.split(',')[1] === action_id.toString();
      });
    },

    find_primary_menu: function (menu_id) {
      return this.find_menu(function (menu){
        return menu.id === menu_id;
      }, true);
    },

    do_push_state: function (state) {
      // States can be pushed without a menu id, in order to keep a
      // menu_id url param present we use the active menu's id.
      if (!state.menu_id && this._primary_menu) {
        state.menu_id = this._primary_menu.id;
      }
      this._super.apply(this, arguments);
    },

    do_menu_action: function (action_id, options) {
      var self = this;
      return this.menu_dm.add(data_manager.load_action(action_id))
        .then(function (result) {
          return self.action_mutex.exec(function () {
            var def = $.Deferred();
            $.when(self.do_action(result, _.extend({}, options, {
              clear_breadcrumbs: true,
            }))).fail(function () {
              def.reject();
            })
            .then(function () {
              def.resolve();
            });

            return def;
          });
        });
    },

    do_menu_id: function (menu_id) {
      if (this._current_menu_id !== menu_id) {
        this._current_menu_id = menu_id;
        this._primary_menu = this.find_primary_menu(menu_id);
        core.bus.trigger('change_primary_menu', this._primary_menu);
      }
    },

    toggle_menu: function (open) {
      if (this.shell.getPane('menu') !== undefined) {
        return this.shell.getPane('menu').toggle(open);
      }

      return $.when();
    },

    toggle_app_menu: function (open) {
      if (this.shell.getPane('app-menu') !== undefined) {
        return this.shell.getPane('app-menu').toggle(open);
      }

      return $.when();
    },

    // --------------------------------------------------------------------------
    // Events handlers
    // --------------------------------------------------------------------------

    on_app_menu_click: function (options) {
      var self = this;
      var action_id = options.action_id;
      if (!action_id) {
        action_id = self.find_nearest_action(options.menu_id);
      }

      var previous_menu_id = this._current_menu_id;
      self.toggle_app_menu(false);
      self.do_menu_id(options.menu_id);
      return this.do_menu_action(action_id)
        .fail(function () {
          self.do_menu_id(previous_menu_id);
        });
    },

    on_menu_click: function (options) {
      var self = this;
      return this.do_menu_action(options.action_id)
        .then(function () {
          self.toggle_menu(false);
        });
    },

    on_hashchange: function (event) {
      if (this._ignore_hashchange) {
        this._ignore_hashchange = false;
        return $.when();
      }

      var self = this;
      return this.clear_uncommitted_changes().then(function () {
        var stringstate = event.getState(false);
        var state = event.getState(true);

        if (state.menu_id) {
          // Change the primary menu and thus primary_menu before doing anything else !!
          self.do_menu_id(state.menu_id);
        }

        if (!_.isEqual(self._current_state, stringstate)) {
          if (state.action || (state.model && (state.view_type || state.id))) {
            state._push_me = false;
            return self.action_manager.do_load_state(state, !!self._current_state).then(function () {
              // Hide both the app and the nav menu
              self.toggle_menu(false);
              self.toggle_app_menu(false);
            }).fail(function () {
              // Could not change state, show the app menu
              self.toggle_app_menu(true);
            });
          } else if (state.menu_id) {
            // Url only contains a menu_id, resolve the root action and perform
            var action_id = self.find_nearest_action(state.menu_id);
            return self.do_action(action_id, { clear_breadcrumbs: true }).then(function () {
              // Hide both the app and the nav menu
              self.toggle_menu(false);
              self.toggle_app_menu(false);
            });
          } else {
            // Could not change state, show the app menu
            self.toggle_app_menu(true);
          }
          self._current_state = stringstate;
        }
      }, function () {
        if (event) {
          self._ignore_hashchange = true;
          window.location = event.originalEvent.oldURL;
        }
      });
    }
  });
  });
