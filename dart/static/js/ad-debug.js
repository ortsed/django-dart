function parse_url( url ) {
    var a = document.createElement('a');
    a.href = url;
    return a;
}

function ad_focus(id){
	$(".ad-debug-layer").removeClass("highlighted-ad");
	var debug_object = $("#" + id + "_debug_layer");
	$(debug_object).addClass("highlighted-ad");
}

$(document).ready(function(){
	$("body").keypress(function(event){
		//Toggled by cntrl-F10
		if (event.which == 63245){
			
			$("body").append("\
<style type=\"text/css\">\
.ad-debug-layer {\
	position:absolute;\
	border:1px solid #000000;\
	background-color: rgb(247, 248, 224);\
	z-index:10000;\
}\
.highlighted-ad {\
	border:2px solid #990000;\
}\
.ad-debug-panel {\
	position:fixed;\
	bottom:0px;\
	width:99%;\
	border-top: 5px solid #333333;\
	background-color:#cccccc;\
	height:400px;\
	overflow:scroll;\
	z-index: 100000;\
	padding: 5px;\
	background-color: #eeeeee;\
}\
.ad-debug-panel-pane{\
	border: 1px solid #333333;\
	margin-bottom:10px;\
	padding: 5px;\
	backgorund-color:#eeeeee;\
}\
</style>\
");
			
			
			if (window.ad_debug){
				window.ad_debug = false;
				$(".ad-debug-layer").remove();
				$(".ad-debug-panel").remove();
			}else {
			
			
				window.ad_debug = true;
				
				$("body").append("<div class=\"ad-debug-panel\"></div>");
				
				$(".ad").each(function(){
				
					if ($(this).attr("id") == ""){
						$(this).attr("id", "ad_debug_" + Math.rand());
					}
					
					var position = $(this).offset();
					var top = position.top;
					var left = position.left;
					var width = $(this).width();
					var height = $(this).height();
					
					var url = $(this).find("script").eq(1).attr("src");
					
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
					
					$("body").append("<div class=\"ad-debug-layer\" id=\"" + $(this).attr("id") + "_debug_layer\" style=\"top:" + top + "px;left:" + left + "px;width:" + width + "px;height:" + height + "px;\"><b>" + zone + ": " + param_dict["pos"] + "</b><br />" + param_dict["sz"] + "<\/div>");
					
					$(".ad-debug-panel").append("<ul class=\"ad-debug-panel-pane\">\
					<li><b>Site:</b> " + site  + "</li>\
					<li><b>Domain:</b> " + domain + "</li>\
					<li><b>Network:</b> " + network  + "</li>\
					<li><b>Zone:</b> " + zone + "</li>\
					<li><b>Position:</b> " + position  + "</li>\
					<li><b>Params:</b> " + params + "</li>\
					<li><b>URL:</b> " + url + "</li>\
					<li><a href=\"#" + $(this).attr("id") + "\" onclick=\"ad_focus('" + $(this).attr("id") + "')\">Highlight</a></li>\
					</ul>");
					
					
				});
			
				
			}			
		
		}
	
	});
});