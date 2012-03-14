from django.contrib import admin
from settings import ADMIN_MEDIA_PREFIX
from dart.models import Zone, Position, Custom_Ad, Custom_Ad_Template, Zone_Position
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

reverse_lazy = lazy(reverse, str)


class Zone_PositionInline(admin.TabularInline):
    model = Zone.position.through

class Zone_Admin(admin.ModelAdmin):
	prepopulated_fields = {"slug" : ('name',)}
	css = {
		'all': (
			ADMIN_MEDIA_PREFIX + 'blog/css/autocomplete.css',
		)
	}
	
	fieldsets = (
		(None, {
			'fields': (
				'name',
				'slug',
			)
		}),
	)
	inlines = [
        Zone_PositionInline,
    ]


class Position_Admin(admin.ModelAdmin):
	prepopulated_fields = {"slug" : ('name',)}
	
	class Media:
		
		js = (
			reverse_lazy("dart_static", args=("position.js",)),
		)
	
	fieldsets = (
		(None, {
			"fields": ("name", "slug", "size", )
		}),
		("Size", {
			"classes": ("collapse closed sizes",),
			"fields": ("width", "height")
		}),
	)

class Custom_Ad_Template_Admin(admin.ModelAdmin):
	pass	
	
class Custom_Ad_Admin(admin.ModelAdmin):
	prepopulated_fields = {"slug" : ('name',)}
		
	class Media:
		
		js = (
			reverse_lazy("dart_static", args=("custom_ad.js",)),
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