from coffin.conf.urls.defaults import *
import os
from django.views.static import serve

urlpatterns = patterns("dart.views",
	
	url(r'^(?P<ad_url>\S+)$', 'ad'),
	
	url(r"template/(?P<template_id>\d+)/$", "custom_ad_template_ajax"),
	
	url(r"^media/(?P<path>.*)$", serve, {"document_root": os.path.dirname(__file__) + "/media"}, "dart_static"),
)
