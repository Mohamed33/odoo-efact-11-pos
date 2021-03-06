odoo.define('vit_dotmatrix.print_button', function (require) {
"use strict";
var form_widget = require('web.FormRenderer');

form_widget.include({
    _addOnClickAction: function ($el, node) {
        var self = this;
        $el.click(function () {

            //MY CODE
            if(node.attrs.custom === "print"){
                var url = "http://localhost:8001/dotmatrix/print";
                var printer_data = self.state.data.printer_data;                
                if (!printer_data){
                    alert('No data to print. Please click Update Printer Data');
                    return;
                }
                console.log(printer_data);

                $.ajax({
                    type: "POST",
                    url: url,
                    data: {
                        printer_data : printer_data
                    },
                    success: function(data) {
                        alert('Success');
                        console.log(data);
                    },
                    error: function(data) {
                        alert('Failed');   
                        console.log(data);
                    },
                });
                return;
            }

            //just code old may use super
            self.trigger_up('button_clicked', {
                attrs: node.attrs,
                record: self.state,
            });
        });
    },
});
});