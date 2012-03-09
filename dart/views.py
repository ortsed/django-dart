from coffin.shortcuts import render_to_response
from coffin.template import RequestContext
from dart.models import Custom_Ad_Template
from django.core import serializers
from django.http import HttpResponse

def ad(request, ad_url):
	"""Function to display an ad.  Currently customized for the thankyou for sharing iframe ad."""
	
	# truncating this so it can"t be passed an arbitrarily long string
	ad_url = "http://ad.doubleclick.net/adj/" + ad_url[:500]
	return render_to_response("dart/sharing_iframe.html", {"ad_url":ad_url}, context_instance=RequestContext(request))


def custom_ad_template_ajax(request, template_id):
	try:
		template = [Custom_Ad_Template.objects.get(id=template_id)]
	except Custom_Ad_Template.DoesNotExist:
		template = {}

	return HttpResponse(serializers.serialize("json", template))