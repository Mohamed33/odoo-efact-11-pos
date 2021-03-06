/**
 * Created by Asus on 1/02/2018.
 */
var nameValido = false;
var emailValido = false;
var mobileValido = false;
var departamentoValido = false;

$("#name , #name1").on("keyup", function() {
    console.log($(this).val());
    if ($(this).val().length >= 3) {
        nameValido = true;
        $(this).css({ 'border': 'solid blue 2px' })
    } else {
        nameValido = false;
        $(this).css({ 'border': 'solid red 2px' })
    }
    validate();
});
$("#departamento").on("keyup", function() {
    console.log($(this).val());
    if ($(this).val().length >= 3) {
        departamentoValido = true;
        $(this).css({ 'border': 'solid blue 2px' })
    } else {
        departamentoValido = false;
        $(this).css({ 'border': 'solid red 2px' })
    }
    validate();
});
$("#email , #email1").on("keyup", function() {
    function validateEmail(email) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    if (validateEmail($(this).val())) {
        emailValido = true;
        $(this).css({ 'border': 'solid blue 2px' })
    } else {
        emailValido = false;
        $(this).css({ 'border': 'solid red 2px' })
    }
    validate();
});
$("#mobile , #mobile1").on("keyup", function() {
    function validateMobile(mobile) {
        var re = /^9[\d]{8}$/;
        return re.test(String(mobile).toLowerCase())
    }
    if (validateMobile($(this).val())) {
        mobileValido = true;
        $(this).css({ 'border': 'solid blue 2px' })
    } else {
        mobileValido = false;
        $(this).css({ 'border': 'solid red 2px' })

    }
    validate();
});

function validate() {
    if (nameValido && mobileValido && emailValido && departamentoValido) {
        $("#submit").removeAttr("disabled")
    } else {
        $("#submit").attr("disabled", "disabled")
    }
}

$("#submit").on("click", function() {
    var params = {
        'name': $("#name").val(),
        'email': $("#email").val(),
        'mobile': $('#mobile').val(),
        'curso_id': $("#curso_id").val(),
        'departamento': $("#departamento").val()
    };

    var data = {
        jsonrpc: "2.0",
        method: "inscripcion",
        params: params,
        id: Math.floor(Math.random() * 1000 * 1000 * 1000)
    };
    $.ajax({
        url: "/inscripcion",
        dataType: "json",
        type: "POST",
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(data) {
            if (data["result"]) {
                $("#msg-html").html(data["result"]['msg']);
                $("#submit").addClass("hidden");
                $("#name").val("");
                $("#email").val("");
                $("#mobile").val("");
                $("#departamento").val("");
            }
        }
    });

});
$("#inscribete_aqui").on("click", function() {
    $("#msg-html").html("");
    $("#submit").removeClass("hidden");
    $("#name").val("");
    $("#email").val("");
    $("#mobile").val("");
    $("#departamento").val("");
});
validate();


/*********************CCOMUNIDAD WE******************************/

$("#submit_comunidad_we").on("click", function() {
    console.log("hola mundo");
    var params = {
        'name': $("#name1").val(),
        'email': $("#email1").val(),
        'mobile': $('#mobile1').val(),
        'dni': $('#dni1').val(),
        'institucion': $('#institucion1').val(),
        'departamento': $("#departamento1").val()
    };

    var data = {
        jsonrpc: "2.0",
        method: "comunidadwe",
        params: params,
        id: Math.floor(Math.random() * 1000 * 1000 * 1000)
    };
    $.ajax({
        url: "/comunidad-we",
        dataType: "json",
        type: "POST",
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(data) {
            if (data["result"]) {
                var html = '<div class="alert alert-success"><strong>Gracias !</strong>' + data["result"]['msg'] + '</div>'
                $("#msg-html1").html(html);
                $("#name1").val("");
                $("#email1").val("");
                $("#mobile1").val("");
                $("#dni1").val("");
                $("#institucion1").val("");
                $("#departamento1").val("");
            }
        }
    });

});