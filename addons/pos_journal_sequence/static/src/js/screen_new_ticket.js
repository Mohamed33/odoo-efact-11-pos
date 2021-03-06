odoo.define('pos_journal_sequence.pos_new_ticket', function(require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var screens = require('point_of_sale.screens');
    var rpc = require("web.rpc")
        //var rpc = require("web.rpc")
        //var Model = require('web.Model')
        //var ReceiptScreenWidget = screens.ReceiptScreenWidget;
        //var ReceiptScreenWidgetSuper = ReceiptScreenWidget;
    var gui = require('point_of_sale.gui');

    screens.ReceiptScreenWidget = screens.ReceiptScreenWidget.extend({
        get_receipt_render_env:function(){
            var order = this.pos.get_order();
            var client = order.get_client();
            var receipt = order.export_for_printing();
            var journal = this.pos.db.get_journal_id(order.get_sale_journal());

            var total_letras = numeroALetras(order.get_total_with_tax(), {
                plural: ' SOLES',
                singular: ' SOL',
            });


            var self = this;

            function descuento(order) {
                var desc = 0;
                order.get_orderlines().forEach(function(orderline) {
                    desc = desc + orderline.price * orderline.quantity * orderline.discount / 100
                })
                return desc
            }

            function total(order) {
                var tot = 0;
                order.get_orderlines().forEach(function(orderline) {
                    tot = tot + orderline.price * orderline.quantity
                })
                return tot
            }
            var d = (new Date());
            
            
            if (journal) {
                var tipo_doc = journal.invoice_type_code_id;
                var serie = journal.code;
                var numero = order.get_number().substring(5, 14);
                //var FECHA_EMISION = order.formatted_validation_date.substring(0, 10);

                var FECHA_EMISION = d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear();
                var TIPO_DOC_REC = client.tipo_documento.toString();
                //CALCULAR IMPUESTOS
                var inafecto = 0.0
                var exonerado = 0.0
                var gravado = 0.0
                var igv = 0.0

                order.get_tax_details().forEach(function(element) {
                    if(element["tax"]["tipo_afectacion_igv_code"]=="10"){
                        igv = element.amount
                    }
                });
                order.get_orderlines().forEach(function(line){
                    line.get_taxes().forEach(function(tax){
                        if(["30","40"].find(function(el){return el == tax.tipo_afectacion_igv_code})){
                            inafecto = inafecto + line.price * line.quantity
                        }
                        if(["20"].find(function(el){return el == tax.tipo_afectacion_igv_code})){
                            exonerado  = exonerado + line.price * line.quantity
                        }
                        if(["10"].find(function(el){return el == tax.tipo_afectacion_igv_code})){
                            gravado  = gravado + line.price * line.quantity
                        }
                    })
                    inafecto = Math.round(inafecto*100)/100
                    exonerado = Math.round(exonerado*100)/100
                    gravado = Math.round(gravado*100)/100
                })
                
                igv = Number(Math.round(igv + 'e2') + 'e-2');
                var texto_qr = self.pos.company.vat + "|" + tipo_doc + "|" + serie + "|" + numero + "|" + igv.toString() + "|" + order.get_total_with_tax().toString() + "|" + FECHA_EMISION + "|" + TIPO_DOC_REC + "|" + client.vat + "|";
                
                return {
                    widget: self,
                    order: order,
                    receipt: receipt,
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                    client: client,
                    total_letra: total_letras,
                    journal: journal,
                    descuento: descuento(order),
                    total: total(order),
                    inafecto: inafecto,
                    exonerado: exonerado,
                    gravado: order.get_total_without_tax()-inafecto-exonerado,
                    igv:igv,
                    fecha_emision: d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear() + " " + d.getHours() + ":" + d.getMinutes(),
                    qr:texto_qr
                }
                
            }else{
                return  {
                    widget: self,
                    order: order,
                    receipt: receipt,
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                    client: client,
                    total_letra: total_letras,
                    journal: journal,
                    descuento: descuento(order),
                    total: total(order),
                    fecha_emision: d.getDate() + "/" + (d.getMonth() + 1) + "/" + d.getFullYear() + " " + d.getHours() + ":" + d.getMinutes()
                };
                
            }
        },
        render_receipt:function() {
            $(".o_loading").hide()
            this._super()
            var res = this.get_receipt_render_env()
            console.log(res)
            jQuery('#qrcode').qrcode({
                width: 80,
                height: 80,
                text: res["qr"]
            });
            
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function() {
                if (!self._locked) {
                    self.click_next();
                }
            });
            this.$('.back').click(function() {
                if (!self._locked) {
                    self.click_back();
                }
            });
            this.$('.button.print').click(function() {
                if (!self._locked) {
                    self.print();
                }
            });
            this.$('.button.print-a4').click(function() {
                let order = self.pos.get_order();
                if (order.number) {
                    rpc.query({
                        model: "account.invoice",
                        method: "search_read",
                        domain: [
                            ["move_name", '=', order.number]
                        ],
                        fields: ["id", "name", "move_name"],
                        limit: 1
                    }).then(function(val) {
                        if (val.length == 1) {
                            let url = '/report/pdf/account.report_invoice/' + val[0].id
                            window.open(url, '_blank');
                        }

                    })

                } else {
                    self.gui.show_popup('Error', {
                        'title': 'Solo puedes imprimir en A4 si es Factura o Boleta / El comprobante aún no ha sido procesado completamente',
                        'body': "",
                    });
                }
            });
        }
    });

    gui.define_screen({name:'receipt', widget: screens.ReceiptScreenWidget});

    return {
        ReceiptScreenWidget:screens.ReceiptScreenWidget
    }
});