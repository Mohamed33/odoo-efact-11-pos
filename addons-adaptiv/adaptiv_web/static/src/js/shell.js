odoo.define('adaptiv_web.shell', function (require) {
"use strict";

var Widget = require('web.Widget');

var AbstractShellPane = Widget.extend({

  defaultOptions: {
    side: 'left',
    size: 'sm',
    template: 'ShellPane',
  },

  init: function(options) {
    this._super(_instance);
    options = _.extend({}, this.defaultOptions, options);
    this._shell = _instance;
    this.isOpen = false;
    this.side = options.side;
    this.size = options.size;
    this.template = options.template;
    this.options = options;
  },

  start: function() {
    this.$el.addClass(this.side + ' ' + this.size);
  },

  destroy: function() {
    delete this._shell.panes[this._id];
    this._shell._update();
    this._super();
  },

  _reflow: function() {
    if (this.isOpen) {
      this.$el.addClass('open');
      this.trigger('opened');
      return this._shell._reflow();
    } else {
      this.$el.removeClass('open');
      this.trigger('closed');
      this._shell._update();
      return $.when();
    }
  },

  open: function() {
    this.isOpen = true;
    return this._reflow();
  },

  close: function() {
    this.isOpen = false;
    return this._reflow();
  },

  toggle: function(open) {
    if (open === undefined) {
      if (this.isOpen) {
        return this.close();
      } else {
        return this.open();
      }
    } else if(open) {
      return this.open();
    } else {
      return this.close();
    }

  },
});

var ShellPane = AbstractShellPane.extend({

  init: function(child, options) {
    this._super(options);
    child.setParent(this);
    this._child = child;
  },

  start: function() {
    this._super();
    return this._child.replace(this.$el.find('.a_pane_content'));
  },

});

var Shell = Widget.extend({
  template: 'Shell',

  events: {
    'click .a_overlay': function (ev) {
      ev.preventDefault();
      this.closeOpenPane();
    }
  },

  init: function(parent, $canvas, options) {
    this._super(parent);
    this.$canvas = $canvas;
    this.panes = {};
    _instance = this;
  },

  start: function() {
    this.$panes = this.$el.find('.a_panes');
    this.$overlay = this.$el.find('.a_overlay');
  },

  _reflow: function(source) {
    if (this._preventReflow) {
      return $.when();
    }

    var self = this;
    this._preventReflow = true;
    var defs = [];
    if (source) {
      // Make sure every pane except source is closed
      defs.concat(_.map(
        _.filter(this.panes, function(pane) {
          return pane !== source;
        }),
        function(pane) {
          return pane.close();
        }
      ));
    }

    return $.when.apply($, defs).then(function() {
      self._preventReflow = false;
      self._update();
    });
  },

  _update: function() {
    var openPane = this.findOpenPane();
    this.$el.add(this.$canvas).removeClass(function(i, classNames) {
      return _.filter(classNames.split(' '), function(className) {
        return className.indexOf('open-') == 0;
      }).join(' ');
    });

    if(openPane !== undefined) {
      this.$el.add(this.$canvas).addClass('open-' + openPane.side);
      if(openPane.size) {
        this.$el.add(this.$canvas).addClass('open-' + openPane.size);
      }
    }
  },

  addPane: function(id, pane) {
    if(this.panes.hasOwnProperty(id)) {
      throw new Error ('Shell pane with this id already exists', id);
    }

    this.panes[id] = pane;
    pane._id = id;
    pane.appendTo(this.$panes);
    return pane;
  },

  getPane: function(id) {
    return this.panes[id];
  },

  findOpenPane: function() {
    return _.find(this.panes, function(pane) {
      return pane.isOpen;
    });
  },

  closeOpenPane: function(id) {
    var pane = this.findOpenPane();
    if(pane !== undefined) {
      return pane.close()
    }

    return $.when();
  },

});

var _instance = null;
var getInstance = function() {
  return _instance;
}

return {
  Shell: Shell,
  ShellPane: ShellPane,
  AbstractShellPane: AbstractShellPane,
  getInstance: getInstance
}
});
