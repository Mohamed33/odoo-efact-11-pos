odoo.define('adaptiv_web.FormRenderer', function(require) {
    "use strict";
    var FormRenderer = require('web.FormRenderer');
    FormRenderer.include({
        // Override in order to display all stat buttons
        _renderButtonBox: function (node) {
            var self = this;
            var $result = $('<' + node.tag + '>', { 'class': 'o_not_full' });
            var buttons = _.map(node.children, function (child) {
                if (child.tag === 'button') {
                    return self._renderStatButton(child);
                } else {
                    return self._renderNode(child);
                }
            });
            var buttons_partition = _.partition(buttons, function ($button) {
                return $button.is('.o_invisible_modifier');
            });
            var invisible_buttons = buttons_partition[0];
            var visible_buttons = buttons_partition[1];

            // Add the buttons
            _.each(visible_buttons, function ($button) {
                $button.appendTo($result);
            });

            this._handleAttributes($result, node);
            this._registerModifiers(node, this.state, $result);
            return $result;
        }
    })
});
