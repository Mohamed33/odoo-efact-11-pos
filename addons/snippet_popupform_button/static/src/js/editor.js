odoo.define('snippet_popupform_button.editor', ["web.rpc", "web.core",
    "web_editor.snippets.options",
    "web.Dialog", "web.ajax"
], function(require) {
    'use strict';

    var core = require('web.core');
    var options = require('web_editor.snippets.options');
    var Dialog = require("web.Dialog");
    var ajax = require("web.ajax");
    var qweb = core.qweb;
    var rpc = require("web.rpc")
        //var Model = require("web.Model");
        //var Curso = new Model("product.template");


    ajax.loadXML('/snippet_popupform_button/static/src/xml/templates.xml', qweb);

    options.registry.snippet_inscribete_opt = options.Class.extend({
        start: function() {
            this._super.apply(this, arguments);
            var self = this;
            /*
            Curso.call("search_read", [
                [],
                ["name"]
            ])*/
            rpc.query({
                model: "product.template",
                method: "search_read",
                args: []
            }).then(function(cursos) {
                console.log(cursos)
                var dialogObject = (new Dialog(null, {
                    title: "Selecciona el Curso",
                    $content: $(core.qweb.render("snippet_popupform_button.elegir_curso", { "cursos": cursos })),
                    buttons: [{
                            text: "Aceptar",
                            click: function() {
                                console.log(this.$content[0].children[0][0].value)
                                self.curso_seleccionado = this.$content[0].children[0][0].value;
                                self.clean_for_save();
                            },
                            close: true
                        },
                        { text: "Cancelar", close: true }
                    ]
                }));
                dialogObject.open();
            });

        },
        clean_for_save: function() {
            this.$target.find("#curso_id").attr("value", this.curso_seleccionado);
        }
    });
    return options

});