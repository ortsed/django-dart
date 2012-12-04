from django.contrib import admin
from settings import ADMIN_MEDIA_PREFIX, STANDARD_ADMIN_MEDIA_PREFIX
from dart.models import Zone, Position, Custom_Ad, Custom_Ad_Template, Zone_Position, Size
from settings import STATIC_URL

try:
	from genericadmin.admin import GenericAdminModelAdmin
except:
	class GenericAdminModelAdmin(admin.ModelAdmin):
		pass
		
class Zone_PositionInline(admin.TabularInline):
	model = Zone.position.through
	ordering = ("position__name",)

	
class Zone_Admin(GenericAdminModelAdmin):
	ordering = ("name",)
	prepopulated_fields = {"slug" : ("name",)}
	
	ct_field = "content_type"
	ct_fk_field = "object_id"
	css = {
		"all": (
			ADMIN_MEDIA_PREFIX + "blog/css/autocomplete.css",
		)
	}
	
	fieldsets = (
		(None, {
			"fields": ("name", "slug", "site"),
		}),
		("Associated Content", {
			"fields": ("content_type", "object_id",)
		}),
	)
	inlines = [
		Zone_PositionInline,
		
	]

class Size_Admin(admin.ModelAdmin):
	ordering = ("name",)


class Zone_Inline(admin.TabularInline):
	model = Zone.position.through
	verbose_name = "Enabled Zones"
	verbose_name_plural = "Enabled Zones"

class Position_Admin(admin.ModelAdmin):
	prepopulated_fields = {"slug" : ("name",)}
	ordering = ("name",)
	class Media:
		
		js = (
			STANDARD_ADMIN_MEDIA_PREFIX + "dart/js/position.js",
		)
	
	fieldsets = (
		(None, {
			"fields": ("name", "slug", "sizes", )
		}),
	)
	
	inlines = [
		Zone_Inline,
		
	]

class Custom_Ad_Template_Admin(admin.ModelAdmin):
	pass	
	
class Custom_Ad_Admin(admin.ModelAdmin):
	prepopulated_fields = {"slug" : ("name",)}
	search_fields = ["name", ]
	
	class Media:
		
		js = (
			STANDARD_ADMIN_MEDIA_PREFIX + "dart/js/custom_ad.js",
		)
	fieldsets = (
		(None, {
			"fields": ("name", "slug", "type" )
		}),
		("Custom Code", {
			"description": "Use this section to write custom HTML. Overrides anything set in the Image/URL section.",
			"classes": ("collapse closed sizes custom-code",),
			"fields": ("load_template", "embed",)
		}),
		("Image/URL", {
			"description": "Upload an image and a URL for a simple linked image ad unit",
			"classes": ("collapse closed sizes image-url",),
			"fields": ("url", "image")
		}),
		("Text Version", {
			"description": "Text version of the ad for non-HTML/JS browsers and newsletters",
			"classes": ("sizes",),
			"fields": ("text_version",)
		}),
	)

admin.site.register(Zone, Zone_Admin)
admin.site.register(Custom_Ad, Custom_Ad_Admin)
admin.site.register(Custom_Ad_Template, Custom_Ad_Template_Admin)
admin.site.register(Position, Position_Admin)
admin.site.register(Size, Size_Admin)