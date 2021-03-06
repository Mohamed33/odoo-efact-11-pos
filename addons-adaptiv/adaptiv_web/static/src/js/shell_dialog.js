odoo.define('adaptiv_web.shell_dialog', function(require) {
  "use strict";

  var core = require('web.core');
  var shell = require('adaptiv_web.shell');
  var AbstractShellPane = shell.AbstractShellPane;
  var getShell = shell.getInstance;

  var Widget = require('web.Widget');
  var Dialog = require('web.Dialog');

  var QWeb = core.qweb;
  var _t = core._t;

  var ShellDialog = Widget.extend({

    template: 'ShellDialog',

    init: function(dialog) {
      this._super(dialog);
      this._dialog = dialog;
    },

    start: function() {
      return this._dialog.replace(this.$el.find('.a_dialog_content'));
    },

    open: function() {
      var self = this;
      return this._pane._dialogOpen(this).then(function() {
        self.trigger('shell.dialog.opened');
      });
    },

    close: function() {
      var self = this;
      return this._pane._dialogClose(this).then(function() {
        self.trigger('shell.dialog.closed');
      })
    },

    show: function() {
      this.$el.removeClass('hidden');
    },

    hide: function() {
      this.$el.addClass('hidden');
    }
  });

  var ShellDialogPane = AbstractShellPane.extend({

    init: function() {
      this._super({
        side: 'right',
        size: 'lg',
        template: 'ShellDialogPane'
      });

      this.dialogs = [];
    },

    close: function() {
      var dialogs = this.dialogs.slice();
      return this._super().then(function() {
        _.each(dialogs, function(dialog) {
          dialog.close();
        });
      });
    },

    _dialogOpen: function(dialog) {
      var self = this;
      return dialog.appendTo(this.$el.find('.a_dialogs')).then(function() {
        return self.open();
      });
    },

    _dialogClose: function(dialog) {
      if(this.dialogs.indexOf(dialog) != -1) {
        this.dialogs.splice(this.dialogs.indexOf(dialog), 1);
      }

      if (this.dialogs.length > 0) {
        this.dialogs[this.dialogs.length - 1].show();
        return $.when();
      } else {
        return this.close();
      }
    },

    addDialog: function(dialog) {
      if (this.dialogs.length > 0) {
        this.dialogs[this.dialogs.length - 1].hide();
      }
      dialog._pane = this;
      this.dialogs.push(dialog);
    }

  });

  Dialog.include({

    getShellDialogClass: function() {
      if (this.size == 'large') {
        return ShellDialog;
      }
    },

    initShellDialog: function() {
      if(!this.shellDialog) {
        var shell = getShell();
        var ShellDialogClass = this.getShellDialogClass();
        if(shell && ShellDialogClass) {
          this.shellDialog = new ShellDialogClass(this);
          var pane = shell.getPane('modal');
          if (!pane) {
            pane = shell.addPane('modal', new ShellDialogPane());
          }

          pane.addDialog(this.shellDialog);
        }
      }
    },

    willStart: function() {
      var self = this;
      return this._super.apply(this, arguments).then(function() {
        // Render modal once xml dependencies are loaded
        if (self.shellDialog) {
          self.startShellDialog();
        } else {
          self.startModal();
        }
      });
    },

    startShellDialog: function() {
      this.$modal = this.shellDialog.$el;
      this.$footer = this.$modal.find(".a_footer_content");
      this.set_buttons(this.buttons);
      this.shellDialog.on('shell.dialog.closed', this, this.destroy);
    },

    startModal: function() {
      this.$modal = $(QWeb.render('Dialog', {
        title: this.title,
        subtitle: this.subtitle,
        technical: this.technical,
      }));
      switch (this.size) {
        case 'large':
          this.$modal.find('.modal-dialog').addClass('modal-lg');
          break;
        case 'small':
          this.$modal.find('.modal-dialog').addClass('modal-sm');
          break;
      }

      this.$footer = this.$modal.find(".modal-footer");
      this.set_buttons(this.buttons);
      this.$modal.on('hidden.bs.modal', _.bind(this.destroy, this));
    },

    renderElement: function() {
      this._super();
      if (this.$content) {
        this.setElement(this.$content);
      }

      if (!this.shellDialog) {
        this.$el.addClass('modal-body');
      } else {
        this.$el.removeClass('modal-body');
      }

      this.$el.addClass(this.dialogClass);
      this.set_title(this.title, this.subtitle);
    },

    set_title: function(title, subtitle) {
      this.title = title || "";
      if (subtitle !== undefined) {
        this.subtitle = subtitle || "";
      }

      var $title;
      if (this.shellDialog) {
        $title = this.shellDialog.$el.find('.a_title').first();
      } else {
        $title = this.$modal.find('.modal-title').first()
      }

      var $subtitle = $title.find('.o_subtitle').detach();
      $title.html(this.title);
      $subtitle.html(this.subtitle).appendTo($title);

      return this;
    },

    open: function() {
      var self = this;
      this.initShellDialog();

      // remove open tooltip if any to prevent them staying when modal is opened
      $('.tooltip').remove();

      if (this.shellDialog) {
        this.shellDialog.open().then(function() {
          self._opened.resolve();
        });
      } else {
        this.appendTo($('<div/>')).then(function () {
          self.$modal.find(".modal-body").replaceWith(self.$el);
          self.$modal.modal('show');
          self._opened.resolve();
        });
      }

      return this;
    },

    destroy: function(reason) {
      if (!this.__closed) {
        this.__closed = true;
        this.trigger("closed", reason);
      }

      if (this.isDestroyed()) {
        return;
      }

      this._super();

      $('.tooltip').remove(); //remove open tooltip if any to prevent them staying when modal has disappeared
      if (this.shellDialog) {
        this.shellDialog.close();
      } else {
        if (this.$modal) {
          this.$modal.modal('hide');
          this.$modal.remove();
        }

        var modals = $('body > .modal').filter(':visible');
        if (modals.length) {
          modals.last().focus();
          // Keep class modal-open (deleted by bootstrap hide fnct) on body to allow scrolling inside the modal
          $('body').addClass('modal-open');
        }
      }
    }

  });

  return {
    ShellDialog: ShellDialog,
    ShellDialogPane: ShellDialogPane
  };

});
