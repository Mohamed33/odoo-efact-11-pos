odoo.define('quinto_sale.DB', ['point_of_sale.DB'], function(require) {
    "use strict";
    var PosDB = require('point_of_sale.DB');

    PosDB.include({
        search_product_in_category: function(category_id, query) {
            var arr = query.split(" ")
            var results = [];
            var results_tmp = []
            var self = this;
            arr.forEach(q => {
                results = []
                let query = q
                try {
                    query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
                    query = query.replace(/ /g, '.+');
                    //list_keyword = query.split(".+").reverse().join(".+")
                    //query = query + ".+" + list_keyword
                    var re = RegExp("([0-9]+):.*?" + query, "gi");
                } catch (e) {
                    results = [];
                }

                for (var i = 0; i < 500; i++) {
                    let r = false
                    if (results_tmp.length == 0) {
                        r = re.exec(self.category_search_string[category_id]);
                        //console.log(self.category_search_string[category_id])
                    } else {
                        let res = results_tmp.map(function(e) { return self._product_search_string(e) }).join("")
                        r = re.exec(res)
                            //console.log(res)
                    }
                    //console.log(this.category_search_string[category_id])
                    if (r) {
                        var id = Number(r[1]);
                        results.push(this.get_product_by_id(id));
                    } else {
                        break;
                    }
                }
                results_tmp = results
            });
            return results;
        },
    })

})