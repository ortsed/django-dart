function parse_url( url ) {
    var a = document.createElement('a');
    a.href = url;
    return a;
}

$(document).ready(function(){
	$("body").keypress(function(event){
		//Toggled by cntrl-F10
		if (event.which == 63245){
			
			$("body").append("\
<style type=\"text/css\">\
.highlighted-ad {\
	position:absolute;\
	border:1px solid #000000;\
	background-color: rgb(247, 248, 224);\
	z-index:10000;\
}</style>\
");
			
			
			if (window.ad_debug){
				window.ad_debug = false;
				$(".highlighted-ad").remove();
			}else {
			
			
				window.ad_debug = true;
				
				$(".ad").each(function(){
					
					var position = $(this).offset();
					var top = position.top;
					var left = position.left;
					var width = $(this).width();
					var height = $(this).height();
					
					var url = $(this).find("script").eq(1).attr("src");
					
					window.debug = url;
					
					var domain = parse_url(url).host;
					var pathname = parse_url(url).pathname;
					var path_sections = pathname.split("/");
					if (path_sections[0] != "adj") {
						var network = path_sections[1];
						var site = path_sections[3];
						var params = path_sections[4];
					}else { 
						var network = "";
						var site = path_sections[2];
						var params = path_sections[3];
					}
					
					var param_sections = params.split(";");
					var zone = param_sections[0];
					var param_dict = []
					for (i=1;i < param_sections.length;i++){
					
						var pair = param_sections[i].split("=");
						param_dict[pair[0]] = pair[1];
					}
					var position = param_dict["pos"];
					
					$("body").append("<div class=\"highlighted-ad\" style=\"top:" + top + "px;left:" + left + "px;width:" + width + "px;height:" + height + "px;\"><b>" + zone + ": " + param_dict["pos"] + "</b><br />" + param_dict["sz"] + "<\/div>");
				});
			
				
			}			
		
		}
	
	});
});