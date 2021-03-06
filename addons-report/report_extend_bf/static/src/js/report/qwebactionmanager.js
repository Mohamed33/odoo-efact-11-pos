odoo.define('report_extend_bf.ext_report', function (require) {
'use strict';

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var session = require('web.session');

var trigger_download = function (session, response, c, action, options) {
    return session.get_file({
        url: '/report/download',
        data: {data: JSON.stringify(response)},
        complete: framework.unblockUI,
        error: c.rpc_error.bind(c),
        success: function () {
            if (action && options && !action.dialog) {
                options.on_close();
            }
        },
    });
};

/**
 * This helper will generate an object containing the report's url (as value)
 * for every qweb-type we support (as key). It's convenient because we may want
 * to use another report's type at some point (for example, when `qweb-pdf` is
 * not available).
 */
var make_report_url = function (action) {
    var report_urls = {
        'controller': "/report/download_document/" + action.report_name
    };
    // We may have to build a query string with `action.data`. It's the place
    // were report's using a wizard to customize the output traditionally put
    // their options.
    if (_.isUndefined(action.data) || _.isNull(action.data) || (_.isObject(action.data) && _.isEmpty(action.data))) {
        if (action.context.active_ids) {
            var active_ids_path = '/' + action.context.active_ids.join(',');
            // Update the report's type - report's url mapping.
            report_urls = _.mapObject(report_urls, function (value, key) {
                return value += active_ids_path;
            });
        }
    } else {
        var serialized_options_path = '?options=' + encodeURIComponent(JSON.stringify(action.data));
        serialized_options_path += '&context=' + encodeURIComponent(JSON.stringify(action.context));
        // Update the report's type - report's url mapping.
        report_urls = _.mapObject(report_urls, function (value, key) {
            return value += serialized_options_path;
        });
    }
    return report_urls;
};


ActionManager.include({
    ir_actions_report: function (action, options) {
        var self = this;
        action = _.clone(action);
        var report_urls = make_report_url(action);
        if (action.report_type === 'controller') {
            framework.blockUI();
            var response = [
                report_urls.controller,
                action.report_type,
            ];
            var c = crash_manager;
            return trigger_download(self.getSession(), response, c, action, options);
        } else {
            return self._super(action, options);
        }
    }
});

});