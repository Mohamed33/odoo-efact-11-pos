odoo.define('lms_website.lms_website', function (require) {
    "use strict";
    require('web.dom_ready');
    var core = require('web.core');
    var _t = core._t;

    $("#lista_de_cursos")
        .on('click',".btn_aniadir_al_carrito",
        function(){
            var product_id = $(this).attr('id')
            $.post("/agregar_producto",{'product_id':product_id})
                .then(function(data){
                    $("#lista_de_cursos #curso_"+product_id).html(data)

                })
            $.post('/modal_continuar_comprando',{"product_id":product_id})
                .then(function(data){
                    $("#continuar_comprando_modal_body").html(data)
                })
        })
    
    $("#lista_de_cursos")    
        .on('click',".btn_quitar_del_carrito",
        function(){
            var product_id = $(this).attr('id')
            $.post("/quitar_producto",{'product_id':product_id})
                .then(function(data){
                    $("#lista_de_cursos #curso_"+product_id).html(data)
                    
                })
        })
    
    $("#continuar_comprando_modal")
        .on('click','.btn_comprar_ahora',
        function(){
            var product_id = $(this).attr('id')
            $.post("/comprar_ahora",{"product_id":product_id})
            .done(function(redirect_url){
                console.log(redirect_url)
                window.location.href = redirect_url
            })
            .fail(function(error){
                console.log(error)
            })
        })

    $("#lista_de_cursos")
        .on("mouseover",".btn_quitar_del_carrito,.btn_aniadido_al_carrito",function(){
            var id = $(this).attr("id")
            $(".btn_"+id).addClass("btn_quitar_del_carrito")
            $(".btn_"+id).removeClass("btn_aniadido_al_carrito")
            
            $(".btn_"+id).text("Quitar del Carrito")
        })

    $("#lista_de_cursos")
        .on("mouseleave",".btn_quitar_del_carrito,.btn_aniadido_al_carrito",function(){
            var id = $(this).attr("id")
            
            $(".btn_"+id).removeClass("btn_quitar_del_carrito")
            $(".btn_"+id).addClass("btn_aniadido_al_carrito")

            $(".btn_"+id).text("Añadido del Carrito")
        })
})