(function($){
	$(function(){
	
		function toggle_section(){
			if ($("#id_type option:selected").val() == 0){
				$(".custom-code").removeClass("closed");
				$(".image-url").addClass("closed");
			}else {
				$(".custom-code").addClass("closed");
				$(".image-url").removeClass("closed");
			}
		}
		
		$("#id_type").change(toggle_section);
		toggle_section();
		
		
		$("#id_load_template").change(function(){
		
			if ($("#id_load_template option:selected").val() != ""){
				if (confirm('Overwrite custom ad code?')){
					$.get("/ajax/admin/dart/template/" + $("#id_load_template option:selected").val() + "/", {}, function(data){
						$("#cke_contents_id_embed iframe").contents().find("body").html(eval(data)[0].fields.template);
					});
				}
			}
		});
	});
}(django.jQuery));