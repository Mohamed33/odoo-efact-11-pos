odoo.define('l10n_pe_pos_consulta_dni_ruc.pos_bus_restaurant', ["point_of_sale.DB","point_of_sale.models","web.core", 'point_of_sale.screens', "web.session", 'point_of_sale.gui', "web.rpc"], function(require) {
    "use strict";
    let session = require("web.session");
    let core = require('web.core');
    let screens = require('point_of_sale.screens');
    let gui = require('point_of_sale.gui');
    //let Model = require('web.Model');
    let rpc = require("web.rpc");
    let _t = core._t;
    var models = require('point_of_sale.models');
    var PosModelSuper = models.PosModel;
    var PosDB = require('point_of_sale.DB');
    //INICIO AGREGADO
    var index = -1;
    for (var i = 0; i < PosModelSuper.prototype.models.length; i++) {
        if (PosModelSuper.prototype.models[i].model == 'res.partner') {
            index = i;
        }
    }
    if (index > -1) {
        PosModelSuper.prototype.models[index].fields.push('tipo_documento');
    }
    //FIN AGREGADO
    PosDB = PosDB.include({
        _partner_search_string: function(partner){
            var str =  partner.name;
            if(partner.barcode){
                str += '|' + partner.barcode;
            }
            if(partner.address){
                str += '|' + partner.address;
            }
            if(partner.phone){
                str += '|' + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += '|' + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += '|' + partner.email;
            }
            if(partner.vat){
                str += '|' + partner.vat;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
        }
    })

    console.log(screens.ClientListScreenWidget.prototype)
    screens.ClientListScreenWidget.include({
        // events:_.assign(screens.ClientListScreenWidget.prototype.events,{
        //     "click .consulta-datos":'get_datos'
        // }),
        rucValido: function(ruc) {
            let ex_regular_ruc;
            ex_regular_ruc = /^\d{11}(?:[-\s]\d{4})?$/;
            if (ex_regular_ruc.test(ruc)) {
                return true
            }
            return false;
        },
        dniValido: function(dni) {
            let ex_regular_dni;
            ex_regular_dni = /^\d{8}(?:[-\s]\d{4})?$/;
            if (ex_regular_dni.test(dni)) {
                return true
            }
            return false;
        },
        saved_client_details2: function(partner_id) {
            let self = this;

            self.reload_partners().then(
                function() {
                    let partner = self.pos.db.get_partner_by_id(partner_id);
                    if (partner) {
                        self.new_client = partner;
                        self.toggle_save_button();
                        self.display_client_details('show', partner);
                    } else {
                        self.display_client_details('hide');
                    }
                },
                function(err, event) {
                    let partner = self.pos.db.get_partner_by_id(partner_id);
                    if (partner) {
                        self.new_client = partner;
                        self.toggle_save_button();
                        self.display_client_details('show', partner);
                    }

                });
        },
        close: function() {
            this._super();
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.hide();
            }
        },
        save_client_details: function(partner) {
            let self = this;
            let fields = {};
            this.$('.client-details-contents .detail').each(function(idx, el) {
                fields[el.name] = el.value || false;
            });
            
            if (!fields.name) {
                this.gui.show_popup('error', _t('A Customer Name Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id = partner.id || false;
            fields.country_id = fields.country_id || false;
            fields.tipo_documento = $('.tipo_doc_group:checked').val();
            if (fields.tipo_documento == '1') {
                fields.company_type = "person"
                if (fields.vat) {
                    if (!self.dniValido(fields.vat)) {
                        self.gui.show_popup('error', {
                            'title': 'Error',
                            'body': "El DNI ingresado es incorrecto",
                        });
                    }
                } else {
                    self.gui.show_popup('error', {
                        'title': 'Error',
                        'body': "Si coloca que el tipo de documento es DNI, ústed debe completar el campo Documento con el DNI del Cliente.",
                    });
                }
            } else if (fields.tipo_documento == '6') {
                fields.company_type = "company"
                if (fields.vat) {
                    if (!self.rucValido(fields.vat)) {
                        self.gui.show_popup('error', {
                            'title': 'Error',
                            'body': "El RUC ingresado es incorrecto",
                        });
                    }
                } else {
                    self.gui.show_popup('error', {
                        'title': 'Error',
                        'body': "Si coloca que el tipo de documento es RUC, ústed debe completar el campo Documento con el DNI del Cliente.",
                    });
                }
            } else {
                fields.tipo_documento = '0'
                fields.company_type = "person"
                if (fields.vat == "") {
                    fields.vat = "-"
                }
            }
            console.log("fields=================")
            console.log(fields)
            console.log("fields=================")
            rpc.query({
                    model: "res.partner",
                    method: "create_from_ui",
                    args: [fields]
                })
                .then(function(partner_id) {
                    self.saved_client_details2(partner_id);
                }, function(err, event) {
                    self.gui.show_popup('error', {
                        'title': _t('Error: Could not Save Changes'),
                        'body': _t('Your Internet connection is probably down.'),
                    });
                }).fail(function(error, event) {
                    if (error.code === 200) {
                        if (error.data.exception_type == 'warning') {
                            delete error.data.debug;
                        }
                        self.gui.show_popup('error-traceback', {
                            'title': "ERROR",
                            'body':  error.data.message
                        });
                    }
                    event.preventDefault();
                });
        },
        get_datos: function() {
            let self = this;
            var tipo_doc = $('.tipo_doc_group:checked').val();
            console.log(tipo_doc)
            console.log($('.tipo_doc_group:checked'))
            // Si es otro tipo de doc. que no sea dni o ruc ya no consulta.
            if (tipo_doc != '-') {
                let fields = {};
                let contents = this.$('.client-details-contents');

                this.$('.detail.vat').each(function(idx, el) {
                    fields[el.name] = el.value || false;
                });
                if (!fields.vat) {
                    this.gui.show_popup('error', {
                        'title': 'Alerta!',
                        'body': 'Ingrese nro. documento',
                    });
                    return;
                };
                let context = {}

                var  customers = this.pos.db.search_partner(fields.vat)
                customers = customers.filter(function(customer){
                    if(customer.tipo_documento==tipo_doc){
                        return true
                    }
                })
                if(customers.length > 0){
                    console.log(customers)  
                    this.display_client_details('edit',customers[0])
                }else{
                    rpc.query({
                        model: "res.partner",
                        method: "consulta_datos",
                        args: [tipo_doc == "1" ? "dni" : "ruc", fields.vat],
                        context: _.extend(context, session.user_context || {})
                    }).then(function(datos) {
                        if (datos.error) {
                            self.gui.show_popup('error', {
                                'title': 'Alerta!',
                                'body': datos.message,
                            });
                        } else if (datos.data) {
                            if (tipo_doc === '1') {
                                contents.find('input[name="name"]').val(datos.data.nombres)
                            } else if (tipo_doc === '6') {
                                contents.find('input[name="name"]').val(datos.data.nombre)
                                contents.find('input[name="zip"]').val(datos.data.ubigeo || "-")
                                contents.find('input[name="street"]').val(datos.data.direccion_completa + "," + datos.data.distrito)
                                contents.find('input[name="city"]').val(datos.data.provincia)
                            }
                        }
                    }).fail(function(error, event) {
                        if (error.code === 200) {
                            if (error.data.exception_type == 'warning') {
                                delete error.data.debug;
                            }
                            self.gui.show_popup('error-traceback', {
                                'title': "ERROR",
                                'body': error.data.message
                            });
                        }
                        event.preventDefault();
                    });
                }
            }
        },
        display_client_details: function(visibility, partner, clickpos) {
            let self = this
            this._super(visibility, partner, clickpos);
            var contents = this.$('.client-details-contents');
            // let contents = this.$('.client-details-contents');
            console.log("consulta-datos")
            console.log($(contents))
            setTimeout(function(){
                console.log($(contents).find(".consultaDatos"))
                $(contents).find(".consultaDatos").on('click',function(ev){console.log("get_Datos");self.get_datos();})
            },2000)
            
            // contents.off('click', '.button .consultaDatos');
            // contents.on('click', '.button .consultaDatos', function() { 
            //     console.log("get-datos")
            //     self.get_datos(); 
            // });
            
        },
    });

    
});