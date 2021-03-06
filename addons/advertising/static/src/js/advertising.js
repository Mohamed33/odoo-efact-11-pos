odoo.define('advertising.page', ['web.Class', 'web.core', 'web.Widget', 'web.utils', 'web.rpc'], function(require) {
    "use strict";
    var Class = require('web.Class');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var utils = require('web.utils');
    var rpc = require('web.rpc')
    var _t = core._t;
    var _lt = core._lt;

    var AdvertisingPage = Widget.extend({
        template: "advertising_page",
        //events: { "click #registros_body>tr>td": "cambiar_resultado" },
        init: function(parent, action) {
            this._super(parent);
            /*
            this.params = action.params
            this.placa_lines = action.params["placa_lines"]
            this.placa_nombre = action.params["placa_nombre"]
            this.fecha_hora = action.params["fecha_hora"]
            this.operador = action.params["operador"]
            this.temperatura = action.params["temperatura"]
            this.numero_lote = action.params["numero_lote"]
            this.cant_kits = action.params["cant_kits"]
            this.cant_negativo_kits = action.params["cant_negativo_kits"]
            this.cant_positivo_kits = action.params["cant_positivo_kits"]
            */
        },
        start: function() {
            var filas = this.placa_lines
            var self = this;
            $.ajax({
                url: "https://escuelafullstack.com",
                type: "GET",
                success: function(data) {
                    $("#pub_and_prom").html(data);
                },
                error: function(data) {
                    alert("Erreur");
                }
            });

            /*
                self.$("#placa_nombre").append("<span><b>Nombre: </b>" + self.placa_nombre + "</span></br>")
                self.$("#fecha_hora").append("<span><b>Fecha y Hora: </b>" + self.fecha_hora + "</span></br>")
                self.$("#operador").append("<span><b>Operador: </b>" + self.operador + "</span></br>")
                self.$("#temperatura").append("<span><b>Temperatura: </b>" + self.temperatura + "</span></br>")
                self.$("#numero_lote").append("<span><b>Número de Lote: </b>" + self.numero_lote + "</span></br>")
                self.$("#cant_kits").append("<span><b>Total de Kits: </b>" + self.cant_kits + "</span></br>")
                self.$("#cant_negativo_kits").append("<span><b>Total Negativos: </b>" + self.cant_negativo_kits + "</span></br>")
                self.$("#cant_positivo_kits").append("<span><b>Total Positivos: </b>" + self.cant_positivo_kits + "</span></br>")

                self.$("#registros_header").empty()
                let tr = self.$("#registros_header").append("<tr/>")
                for (var i = 0; i <= 12; i++) {
                    if (i != 0) {
                        tr.append("<td><b>#" + i + "</b></td>")
                    } else {
                        tr.append("<td></td>")
                    }

                }
                filas.forEach((fila, f) => {
                    self.$("#registros_body").append("<tr id='fila_" + f + "'/>")
                    var row_data = self.$("#registros_body>tr[id='fila_" + f + "']")
                    let tds = "<td>" + String.fromCharCode(65 + f) + "</td>"
                    fila.forEach((el, e) => {
                        if (el["placa_line_kit_id"]) {
                            if (el["placa_line_resultado"] == "Negativo") {
                                tds = tds + "<td style='color:green' data-id='" + el["placa_line_id"] + "' data-resultado='" + el["placa_line_resultado"] + "'>" + el["placa_line_kit_name"] + "</td>"
                            } else if (el["placa_line_resultado"] == "Positivo") {
                                tds = tds + "<td style='color:red' data-id='" + el["placa_line_id"] + "' data-resultado='" + el["placa_line_resultado"] + "'>" + el["placa_line_kit_name"] + "</td>"
                            }
                        } else {
                            tds = tds + "<td data-id='-' style='color:lightgray'>Vacío</td>"
                        }
                    })
                    row_data.append(tds)
                });
            */
        },
        cambiar_resultado: function(ev) {
            /*
            console.log(ev)
            console.log($(ev.toElement).data("id"))
            console.log($(ev.toElement).data("resultado"))

            var resultado = $(ev.toElement).data("resultado");
            if (resultado == "Negativo") {
                resultado = "Positivo"
            } else if (resultado == "Positivo") {
                resultado = "Negativo"
            }

            if ($(ev.toElement).data("id") != "-") {
                rpc.query({
                    model: "hope.placa_line",
                    method: "cambiar_resultado",
                    args: [
                        [$(ev.toElement).data("id")], resultado

                    ]
                }).then(function(res) {
                    console.log(res)
                    if (res) {
                        $(ev.toElement).data("resultado", resultado)
                        console.log(resultado)
                        if (resultado == "Negativo") {
                            $(ev.toElement).css("color", "green")
                        } else if (resultado == "Positivo") {
                            $(ev.toElement).css("color", "red")
                        }
                    }
                })
            }
            */
            /*
            rpc.query({
                model: "pos.order",
                method: "create_from_ui",
                args: [_.map(orders, function(order) {
                    order.to_invoice = options.to_invoice || false;
                    return order;
                })]
            }).then(function(server_ids) {
                _.each(order_ids_to_sync, function(order_id) {
                    self.db.remove_order(order_id);
                });
                self.set('failed', false);
                return server_ids;
            */
        }
    });

    core.action_registry.add('advertising_page', AdvertisingPage);

});