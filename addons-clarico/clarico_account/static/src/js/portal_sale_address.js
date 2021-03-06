$(document).ready(function(){ 
 	$('.o_portal_my_details > div > address > div > div > span').each(function(){
    $(this).html($(this).html().replace(/&nbsp;/gi,''));
	});
});


