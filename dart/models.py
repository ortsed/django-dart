from django.db import models
from cropduster.models import CropDusterField
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField
from coffin.template import Context, loader

from settings import UPLOAD_PATH

STANDARD_AD_SIZES = (
	(0, "Any Size | 0x0"),
	(1, "Custom Size"),
	(2, "Large Rectangle | 336x280"),
	(3, "Medium Rectangle | 300x250"),
	(4, "Square Pop-up | 250x250"),
	(5, "Vertical Rectangle | 240x400"),
	(6, "Rectangle | 180x150"),
	(7, "Leaderboard | 728x90"),
	(8, "Full Banner | 468x60"),
	(9, "Half Banner | 234x60"),
	(10, "Button 1 | 120x90"),
	(11, "Button 2 | 120x60"),
	(12, "Micro Bar | 88x31"),
	(13, "Micro Button | 80x15"),
	(14, "Vertical Banner | 120x240"),
	(15, "Square Button | 125x125"),
	(16, "Skyscraper | 120x600"),
	(17, "Wide Skyscraper | 160x600"),
	(18, "Half-Page | 300x600")
)

CUSTOM_AD_TYPES = (
	(0, "Custom HTML"),
	(1, "Image/URL")
)

class Position(models.Model):

	name = models.CharField(max_length=255) 

	slug = models.CharField(max_length=255) 

	size = models.IntegerField(choices=STANDARD_AD_SIZES, default=0)

	width = models.IntegerField(default=0, null=False, blank=False, help_text="Use zero for unknown/variable values")
	
	height = models.IntegerField(default=0, null=False, blank=False, help_text="Use zero for unknown/variable values")

	class Meta:
		verbose_name_plural = "Ad Positions"
		
	def __unicode__(self):
		return u"%s" % self.name
		
class Zone(models.Model):

	name = models.CharField(max_length=255) 

	slug = models.CharField(max_length=255)
	
	position = models.ManyToManyField(Position, through="Zone_Position")

	class Meta:
		verbose_name_plural = "Ad Zones"
		
	def __unicode__(self):
		return u"%s" % self.name		

class Custom_Ad(models.Model):

	name = models.CharField(max_length=255, default="")
	
	slug = models.CharField(max_length=255)
	
	type =  models.IntegerField(choices=CUSTOM_AD_TYPES, default=0)
	
	url = models.URLField(null=True, blank=True, help_text="Click tag link")
	
	image = models.ImageField(null=True, blank=True, upload_to=UPLOAD_PATH + "custom_ads", help_text="Image for custom ad")
	
	embed = RichTextField(null=True, blank=True)
	
	load_template = models.ForeignKey("Custom_Ad_Template", null=True, blank=True, default=None, help_text="Load HTML code into the embed field from a pre-defined template")
	
	text_version = models.TextField(blank=True, help_text="Text version of ad for newsletters or Javascript disabled browsers")

	class Meta:
		verbose_name = "Custom Ad"
		verbose_name_plural = "Custom Ads"
		
	def __unicode__(self):
		return u"%s" % self.name
		
class Custom_Ad_Template(models.Model):
	""" Templates for creating custom ads """
	class Meta:
		verbose_name = "Custom Ad Template"
		verbose_name_plural = "Custom Ad Templates"
		
	name = models.CharField(max_length=255, default="")
	
	template = RichTextField(null=True, blank=True)

	def __unicode__(self):
		return u"%s" % self.name

	

class Zone_Position(models.Model):

	position = models.ForeignKey(Position)
	
	zone = models.ForeignKey(Zone)
	
	custom_ad = models.ForeignKey(Custom_Ad, blank=True, null=True,)
	
	def __unicode__(self):
		return u"%s: %s" % (self.zone, self.position)
	
	class Meta:
		verbose_name = "Enabled Position"
		verbose_name_plural = "Enabled Positions"

		

class Ad_Page(object):
	""" Base class for Ad and Ad_Factory, keeps track of assigned attributes """
	
	attributes = {}
	_tile = 0
	site = None
	zone = None
	default_render_js = True
	disable_ad_manager = True

	def __init__(self, settings={}, site=None, zone=None, default_render_js=None, disable_ad_manager=None, *args, **kwargs):
		""" Updates default ad page attributes
			site - DART site 
			zone - DART zone
			default_render_js - render DART javascript by default, otherwise blank
			disable_ad_manager - Turn off ad management
			
			Kwargs are passed to DART string. Can be any key, value pair
			
		"""
		for setting in settings:
			self.__setattr__(setting, settings[setting])
		
		if site: self.site = site
		if zone: self.zone = zone
		if default_render_js: self.default_render_js = default_render_js
		if disable_ad_manager: self.disable_ad_manager = disable_ad_manager
	
		self.attributes.update(**kwargs)
		
		
			
	def tile(self):
		self._tile = self._tile + 1
		return self._tile
		

	def get_link(self, **kwargs):
		link = "%s/%s;" % (self.site, self.zone)

		for attr, val in self.attributes.items() + kwargs.items():
			if attr == "title":
				continue
			# if it is a non-string iteratible object
			if hasattr(val, "__iter__"):
				link += self._format_multiple_values(attr, val)
			else:
				link += self._format_value(attr, val)

		return link

	def _format_value(self, attribute_name, val):

		if attribute_name != "sz":
			val = slugify(val)

		return "%s=%s;" % (attribute_name, val)

	def _format_multiple_values(self, attr, values):

		formatted = ""
		index = ""
		for val in values:
			enumerated_attr = attr + str(index)
			formatted += self._format_value(enumerated_attr, val)

			if index == "":
				index = 1
				
			index += 1

		return formatted
	
	
	def has_ad(self, pos, custom_ad=False, **kwargs):
		try:
			qs = Zone_Position.objects.all().filter(position__slug=pos, zone__slug__in=(self.zone,"ros"))
			if custom_ad:
				qs = qs.filter(custom_ad__isnull=False)
			return qs[0]
		except:
			return None
			
	def _iframe_url(self, pos, size, **kwargs):
		
		self.attributes["pos"] = pos
		self.attributes["sz"] = size
		link = "/ad/" + self.get_link(**kwargs)

		return link
		
	def get_custom_ad(self, slug, pos, **kwargs):
		try:
			custom_ad = Custom_Ad.objects.get(slug=slug)
			return _render_custom_ad(pos, custom_ad, **kwargs)
			
		except Custom_Ad.DoesNotExist:
			return ""
			
	
	def _render_custom_ad(self, pos, custom_ad, text_version=False, desc_text="", **kwargs):
		if text_version:
			return custom_ad.text_version
		elif custom_ad.embed:
			return custom_ad.embed
		else :
			t = loader.get_template("dart/embed.html")
			c = Context({
				"pos": pos,
				"link": custom_ad.url,
				"image": custom_ad.image,
				"desc_text": desc_text
			})
			return t.render(c)
			
	def _render_js_ad(self, pos, size="0x0", template="dart/ad.html", desc_text="", **kwargs):
		
		self.attributes["pos"] = pos
		self.attributes["sz"] = size
		link = self.get_link(**kwargs)
		
		context_vars = {
			"pos": pos,
			"link": link,
			"tile": self.tile(),
			"desc_text": desc_text
		}
		context_vars.update(kwargs)
		
		t = loader.get_template(template)
		c = Context(context_vars)
		return t.render(c)
		
		
		
	def _render_default(self, pos, **kwargs):
		if self.default_render_js:
			return self._render_js_ad(pos, **kwargs)
		else:
			return ""
			
			
		
	def get(self, pos, ad=None, enable_ad_manager=None, custom_only=False, **kwargs):
		""" Main class to get ad tag """
		""" 
		Configuration variables used in this function:
			pos -- Ad position slug as defined in Zone_Position
			ad -- A predefined ad, if needed
			custom_only -- Only deliver a custom ad, don't use DART
		
		Standard keywords passed on to template and other functions:
			size -- Limit ads by size, 0x0 is a wildcard
			template -- Template used to render the ad, defaults to basic JS embed
			desc_text -- Text that comes before ad, declaring who the sponsor is
			text_version -- Only deliver text version for a custom ad
		
		"""

		# If ad manager is disabled, it goes straight to displaying the iframe/js code

		if self.disable_ad_manager and not enable_ad_manager:	
			return self._render_default(pos, **kwargs)
		else:
			if not ad:
				ad = self.has_ad(pos, **kwargs)
				
			if ad and ad.custom_ad and not custom_only:
				return self._render_custom_ad(pos, ad.custom_ad, **kwargs)
			else:
				return self._render_default(pos, **kwargs)

