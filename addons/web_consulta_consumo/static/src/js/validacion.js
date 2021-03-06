    function valida_datos() {
        var identificador = $("#identificador").val()
            //var codigocomensal = $("#codigocomensal").val()
        var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;

        if (identificador == "") {
            document.getElementById("pos_orders").innerHTML = '<div class="alert alert-danger"><a href="" class="close" data-dismiss="alert">&times</a>Ingresa datos</div>'
                //$("#codigocomensal").focus();
            $("#identificador").focus();
            return false;
        } else {
            document.getElementById("pos_orders").innerHTML = "";
        }
        if (identificador == "identificador") {
            document.getElementById("pos_orders").innerHTML = '<div class="alert alert-danger"><a href="" class="close" data-dismiss="alert">&times</a>Ingresa datos correctos</div>'
                //$("#codigocomensal").focus();
            $("#identificador").focus();
            return false;
        } else {
            document.getElementById("pos_orders").innerHTML = "";
        }
        if (identificador == "") {
            document.getElementById("pos_orders").innerHTML = '<div class="alert alert-danger"><a href="" class="close" data-dismiss="alert">&times</a>Ingresa su identificador</div>'
            $("#identificador").focus();
            return false;
        } else {
            document.getElementById("pos_orders").innerHTML = "";
        }

        var data = {
            "identificador": $("#identificador").val(),
            "date1": $("#date1").val(),
            "date2": $("#date2").val(),
            'csrf_token':$("#csrf_token").val()
        }
        $.post("/consultaConsumo", data).done(function(response) {
            $("#pos_orders").html(response)
        })
    }