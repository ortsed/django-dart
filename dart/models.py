from django.db import models
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField
from coffin.template import Context, loader
from django.conf import settings
from settings import UPLOAD_PATH
from time import mktime
from datetime import datetime



CUSTOM_AD_TYPES = (
	(0, "Custom HTML"),
	(1, "Image/URL")
)

DART_DOMAIN = getattr(settings, "DART_DOMAIN", "ad.doubleclick.net")

DART_AD_DEFAULTS = getattr(settings, "DART_AD_DEFAULTS", settings.DART_AD_DEFAULTS)


class Size(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False) 
	
	width = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Use zero for unknown/variable values")
	
	height = models.PositiveSmallIntegerField(default=0, null=False, blank=False, help_text="Use zero for unknown/variable values")
	
	def __unicode__(self):
		return u"%s - %s" % (self.name, self.dart_formatted_size)
	
	@property
	def dart_formatted_size(self):
		return u"%sx%s" % (self.width, self.height)

class Position(models.Model):

	name = models.CharField(max_length=255, null=False, blank=False) 

	slug = models.CharField(max_length=255, null=False, blank=False)
	
	sizes = models.ManyToManyField("Size", null=False, blank=False)

	class Meta:
		verbose_name_plural = "Ad Positions"
		
	def __unicode__(self):
		return u"%s" % self.name
		
	@property
	def size_list(self):
		return ",".join([size.dart_formatted_size for size in self.sizes.all()])

		
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
	
	url = models.URLField(null=True, blank=True, help_text="Click tag URL")
	
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
	
	enabled = models.BooleanField(default=True)
	
	def __unicode__(self):
		return u"%s: %s" % (self.zone, self.position)
	
	class Meta:
		verbose_name = "Enabled Position"
		verbose_name_plural = "Enabled Positions"


class Ad_Page(object):
	""" Base class for ad settings on a page """
	
	attributes = {}
	_tile = 0
	site = None
	zone = None
	default_render_js = True
	disable_ad_manager = True
	page_ads = {}

	def __init__(self, settings={}, site=None, zone=None, default_render_js=None, disable_ad_manager=None, *args, **kwargs):
		""" 
		Ad page attributes that are configured here:
			site - DART site - string
			zone - DART zone - string
			default_render_js - render DART javascript by default, otherwise blank - boolean
			disable_ad_manager - Turn off ad management - boolean
			
			Kwargs are passed to DART string. Can be any key, value pair - dict
			
		"""
		DART_AD_DEFAULTS.update(settings)
		
		for setting in DART_AD_DEFAULTS:
			self.__setattr__(setting, DART_AD_DEFAULTS[setting])
		
		if site: self.site = site
		if zone: self.zone = zone
		if default_render_js: self.default_render_js = default_render_js
		if disable_ad_manager: self.disable_ad_manager = disable_ad_manager
	
		if kwargs:
			self.attributes.update(kwargs)
		
		# Pre-load all of the ads for the page into a dict
		if not self.disable_ad_manager:
			page_ads = Zone_Position.objects.all().filter(zone__slug__in=(self.zone,"ros"), enabled=True)
			for ad in page_ads:
				self.page_ads[ad.position.slug] = ad

	@property
	def tile(self):
		""" Gets and increments the tile position for the page """
		self._tile = self._tile + 1
		return self._tile

	
	def has_ad(self, pos, custom_ad=False, **kwargs):
		""" Doesn't render an ad, just checks for existence in ad manager """
		try:
			qs = Zone_Position.objects.all().filter(position__slug=pos, zone__slug__in=(self.zone,"ros"), enabled=True)
			if custom_ad:
				qs = qs.filter(custom_ad__isnull=False)
			return qs[0]
		except:
			return None
			
	def get_custom_ad(self, slug, pos, **kwargs):
		""" Gets custom ad code if it exists """
		try:
			custom_ad = Custom_Ad.objects.get(slug=slug)
			return render_custom_ad(pos, custom_ad, **kwargs)
			
		except Custom_Ad.DoesNotExist:
			return ""
			
	
	def render_custom_ad(self, pos, custom_ad, template="dart/embed.html", text_version=False, desc_text="", **kwargs):
		""" Renders the custom ad, determining which template to use based on custom ad settings """
	
		if text_version:
			return custom_ad.text_version
			
		elif custom_ad.embed:
			return custom_ad.embed
		
		elif custom_ad.url:
			t = loader.get_template(template)
			c = Context({
				"pos": pos,
				"link_url": custom_ad.url,
				"image": custom_ad.image,
				"desc_text": desc_text
			})
			return t.render(c)
		else:
			return ""
			
	def render_js_ad(self, pos, template="dart/ad.html", desc_text="", **kwargs):
		""" 
			Renders a DART JS tag to the ad HTML template 
		"""
		
		context_vars = {
			"js_url": self.js_url(pos, **kwargs),
			"link_url": self.link_url(pos, **kwargs),
			"image_url": self.image_url(pos, **kwargs),
			"tile": self.tile,
			"desc_text": desc_text
		}

		t = loader.get_template(template)
		c = Context(context_vars)
		return t.render(c)
		
		
		
	def render_default(self, pos, custom_only=False, **kwargs):
		"""  
			Renders default ad content, blank or DART javascript,
			depending on settings 
		"""
	
		if self.default_render_js and not custom_only:
			return self.render_js_ad(pos, **kwargs)
		else:
			return ""

	def get(self, pos, ad=None, enable_ad_manager=None, **kwargs):
		return self.render_ad(pos, ad, enable_ad_manager, **kwargs) 
		
	def render_ad(self, pos, ad=None, enable_ad_manager=None, **kwargs):
		""" 
		Main method to display ad code
		
		Configuration variables used in this function
		
			Required:
				pos -- Ad position slug as defined in Zone_Position - string
			
			Optional:
				ad -- A predefined ad, if needed - Ad object
				custom_only -- Only deliver a custom ad, don't use DART - boolean
				enable_ad_manager -- Override page settings and use the ad manager - boolean 
	
			
			Standard keywords passed on to template and other functions:
				size -- Limit ads by size, 0x0 is a wildcard - string
				template -- Template used to render the ad, defaults to basic JS embed - filename string
				desc_text -- Text that comes before ad, declaring who the sponsor is - string
				text_version -- Only deliver text version for a custom ad - boolean
		
		"""

		# If ad manager is disabled, it goes straight to displaying the iframe/js code
		if self.disable_ad_manager and not enable_ad_manager:	
			return self.render_default(pos, **kwargs)
		else:
		
			# using the ad manager
		
			if not ad:
				# if no ad info, get ad info
				
				if enable_ad_manager and not self.page_ads:
					ad = self.has_ad(pos, **kwargs)
				elif pos in self.page_ads:
					ad = self.page_ads[pos]
				
			if ad and ad.custom_ad:
				# if we have an ad, and its a custom one
				return self.render_custom_ad(pos, ad.custom_ad, **kwargs)
				
			elif ad and not ad.custom_ad:
				# if we have an ad
				if "size" not in kwargs:
					kwargs["size"] = ad.position.size_list
				return self.render_js_ad(pos, **kwargs)

			else:
				return self.render_default(pos, **kwargs)
	
	
	# Methods to format DART URLs
	
	def param_string(self, pos, **kwargs):
		""" 
			Formats the DART URL from a set of keyword arguments and settings 
		
			Attributes are defined in order of explicity
				More explicit overrides more general
				default -> zone attributes -> kwargs
		"""
		
		attrs = {
			"size": "0x0",
			"pos": pos,
		}
		attrs.update(self.attributes)
		attrs.update(kwargs)

	
		url = "%s/%s;" % (self.site, self.zone)

		for attr, val in attrs.items():
			if attr == "title":
				continue
				
			# if it is a non-string iteratible object
			if hasattr(val, "__iter__"):
				url += self.format_multiple_values(attr, val)
			else:
				url += self.format_value(attr, val)
		return url
	
	def format_url(self, pos, ad_type, **kwargs):
		""" Formats the DART URL from a set of keyword arguments and settings """
		
		url = self.param_string(pos, **kwargs)
		return "http://%s/%s/%stile=%s;" % (DART_DOMAIN, ad_type, url, self.tile)
	
	def js_url(self, pos, **kwargs):
		""" Gets the DART URL for a Javascript ad """
		""" with_ord -- whether to spit out the ord var in the string """
		
		
		url = self.format_url(pos, "adj", **kwargs)
		if "with_ord" in kwargs:
			url = u"%sord=%s" % (url, int(mktime(datetime.now().timetuple())))
		
		return url

	def iframe_url(self, pos, **kwargs):
		""" Gets the DART URL for an Iframe ad """
		return self.format_url(pos, "ad", **kwargs)
		
	def image_url(self, pos, **kwargs):
		""" Gets the DART URL for an image src """
		return self.format_url(pos, "ad", **kwargs)
		
	def link_url(self, pos, **kwargs):
		""" Gets the DART URL for a link used in HTML ads """
		return self.format_url(pos, "jump", **kwargs)

	def format_value(self, attr, val):
		""" Formats a dict keyword into a DART URL parameter """

		if attr == "size":
			# DART needs size var explicitly spelled 'sz'
			attr = "sz"
		else:
			val = slugify(val)

		return "%s=%s;" % (attr, val)

	def format_multiple_values(self, attr, values):
		""" Formats a dict keyword array into DART URL parameters """

		formatted = ""
		index = ""
		for val in values:
			enumerated_attr = attr + str(index)
			formatted += self.format_value(enumerated_attr, val)

			if index == "":
				index = 1
				
			index += 1

		return formatted

