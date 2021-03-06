function crear(){
    console.log("crear instancia");
    var data = {
        "nombre" : $("#nombre").val(),
    }
    $.post("/crear_instancia", data).done(function(response) {
        $("#message-box").append(response);
            })
}

function instalar(){
    console.log("instalar");
    var data = {
        "nombre" : $("#nombre").val(),
    }
    $.post("/instalar", data).done(function(response) {
        $("#message-box").append(response);
            })
}

function get_status2(){
    console.log("get status");
    var data = {
        "nombre" : $("#nombre").val(),
    }
    $.post("/get_status", data).done(function(response) {
        $("#message-box").append(response);
        $("#message-box").append(response);
            })
}

function get_status(){
    console.log("get status");
    var data = {
        "nombre" : $("#nombre").val(),
    }

    $.ajax({
    url: '/get_status',
    type: 'post',
    success: function(data){
    console.log(data);
    $("#message-box").append("succes");
   // Perform operation on return value
        return data;
    },
    complete:function(data){
    console.log(data+"completo");
            //setTimeout(get_status,5000);
            $("#message-box").append("hola");
            $("#message-box").append(data);
    }
 });
}

$(document).ready(function(){
            // Smart Wizard events
            $("#smartwizard").on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {
                //$("#message-box").append("<br /> > <strong>leaveStep</strong> called on " + stepNumber + ". Direction: " + stepDirection);
                if(stepNumber=='1' && stepDirection=='forward'){
                    $("#message-box").append("creando una instancia");
                    crear();
                }
                if(stepNumber=='2' && stepDirection=='forward'){
                    $("#message-box").append("Instalando modulos");
                    instalar();
                }
            });

            //setTimeout(get_status,5000);


            // Toolbar extra buttons
            var btnFinish = $('<button></button>').text('Finish')
                                             .addClass('btn btn-info')
                                             .on('click', function(){ alert('Finish Clicked'); });
            var btnCancel = $('<button></button>').text('Cancel')
                                             .addClass('btn btn-danger')
                                             .on('click', function(){ $('#smartwizard').smartWizard("reset"); });
            // Smart Wizard initialize
            $('#smartwizard').smartWizard({
                    selected: 0,
                    theme: 'dots',
                    transitionEffect:'fade',
                    toolbarSettings: {toolbarPosition: 'bottom',
                                      toolbarExtraButtons: [btnFinish, btnCancel]
                                    }
                 });


        });


