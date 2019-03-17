$(document).ready(function() {
	function getCookie(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie !== '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) === (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}
	
	$(".play-round").click(function(e){
		e.preventDefault();
		e.stopPropagation();
		if($(this).hasClass("disabled")){
			return;
		}else{
			bet_value_json = {}
			var illegeal_values = false;
			$('.player_bet_value').each(function(i, obj) {
				console.log($(this).val(), $(this).attr("max"))
				if(parseFloat($(this).val()) <= parseFloat($(this).attr("max"))){
					bet_value_json[$(this).attr("id")] = $(this).val();
				}else{
					var alert = $(this).next();
					alert.removeClass("d-none");
					window.setTimeout(function(){
						alert.addClass('d-none');
				    }, 5000);
					illegeal_values = true;
				}
			});
			if(illegeal_values){
				return;
			}
			var formData = {
             	"bet_value": JSON.stringify(bet_value_json),
             	"csrfmiddlewaretoken": getCookie("csrftoken") 
     	    }
			$.ajax({
                type: "POST",
                url: "/table/" + $(this).attr('id')+ "/start-play/",
                data: formData,
                beforeSend: function() {
                	$(".play-round").addClass("disabled btn-secondary").removeClass("btn-primary");
                	$(".player-unjoin").addClass("d-none");
                },
                success: function(data) {
                	data = JSON.parse(data)
                	$(".player-status-wrapper").html(data["player_html"])
                	$(".current-round-wrapper").html(data["round_html"])
                },
                error: function(xhr) {
                },
                complete: function() {
                }
            });
		}
	});
});