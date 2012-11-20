Django-DART
===========
DoubleClick Ad Generator
------------------------

A simple Django application for generating DoubleClick adtags inside of Django templates.

##Optional installation:
	genericadmin: https://github.com/jschrewe/django-genericadmin

###Defaults
Defaults are set inside of settings.py, and should at a minimum contain the 'site' and a default fallback zone

    DART_AD_DEFAULTS = {
        "site":"testsite",
        "zone":"misc",
        "disable_ad_manager": True
        # etc...
    }

Config vars:
    site -- DART site name
    zone -- DART zone for the page or section ads to be displayed.
    disable_ad_manager -- don't use the app's interface to enable disable ads.  
    If so, the app simply renders the Javascript code for all positions.
    default_render_js -- Toggle whether the default is to render DART Javascript code, or nothing.


###In the views
In the view, load an instance of the Ad_Page model that will control the ad tags for that page, 
and then pass that variable to the template.

    from dart.models import Ad_page
    ads = Ad_Page(settings={"default_render_js": True}, zone=zone)
    


###In templates
In the templates you can get the ad tag with the get method of the ad page and the ad position, 
passing any additional variables for that tag at the same time.


    {{ ads.get("leaderboard", size="728x90", template="dart/ad.html") }}




