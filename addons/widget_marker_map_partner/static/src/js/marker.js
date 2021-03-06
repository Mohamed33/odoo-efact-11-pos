odoo.define("widget_marker_map_partner.widget_marker_map_partner",function(require){
    "use strict";
    var AbstractField = require("web.AbstractField")
    var registry  = require("web.field_registry")
    var core = require("web.core")
    var qweb = core.qweb
    var rpc = require("web.rpc")

    
    var WidgetMarkerMapPartner = AbstractField.extend({
        template:"widget_marker_map_partner",
        supportedFieldTypes:["char"],
        events:{
            "click .marker_maps":"get_marker_maps"
        },
        init:function(){
            this._super.apply(this,arguments)
            this.api_key = ""
            this.map = null
            var ubicacion = this.value
            this.zoom = 15
            if(ubicacion){
                if(ubicacion.split("|").length==2){
                    this.lat = parseFloat(ubicacion.split("|")[1])
                    this.lng = parseFloat(ubicacion.split("|")[0])
                    return;
                }
            }
            this.lat = -11.978485
            this.lng = -77.0009887
            return;
        },
        start:function(){
            var self = this
            self._render()
        },
        get_marker_maps:function(ev){
            var self = this;
            if("geolocation" in navigator){
                navigator.geolocation.getCurrentPosition(function(position) {
                    self.lng = position.coords.longitude
                    self.lat = position.coords.latitude
                    self.zoom = 20
                    $(self.$el).find(".message").text("position:"+String(position))
                    let ubicacion = String(self.lng)+"|"+String(self.lat)
                    self._setValue(ubicacion)
                    self._render()
                  },function(err){
                    $(self.$el).find(".message").text("err:"+err.message)
                  })
                //   $(self.$el).find(".message").text(String("geolocation" in navigator))
            }else{
                $(self.$el).find(".message").text("No se puede obtener la geolocalización")
                console.log("No se puede obtener la geolocalización")
            }
        },
        _render:function(){
            var self = this
            self.map = new google.maps.Map($(self.$el).find(".map")[0], {
                zoom:self.zoom,
                center: { lat:self.lat, lng:self.lng }
            });

            self.marker = new google.maps.Marker({
                map:self.map,
                draggable: true,
                animation: google.maps.Animation.DROP,
                position: { lat:self.lat, lng :self.lng}
            });
            // self.marker.addListener("change", function(ev){
            //     console.log(ev)
            // });
            self.map.addListener("dblclick",function(event){
                self.lng = event.latLng.lng()
                self.lat = event.latLng.lat()
                self.zoom = self.map.getZoom()
                
                self.marker.setPosition({lng:self.lng,lat:self.lat})
                let ubicacion = String(self.lng)+"|"+String(self.lat)
                self._setValue(ubicacion)
            })
            self.marker.addListener('dragend', function(event) {
                // setTimeout(function(){
                    let position = self.marker.getPosition()
                    self.lat = position.lat()
                    self.lng = position.lng()
                    let ubicacion = String(self.lng)+"|"+String(self.lat)
                    self._setValue(ubicacion)
                // },1500)
              });
            // self.map.addListener('change', function(event) {
            //     console.log(event)
            //     console.log(self.marker.getPosition())
            // });
        }
    })

    registry.add("widget_marker_map_partner",WidgetMarkerMapPartner)
})