import httplib, re
from django.conf import settings
from dart.models import Zone, DART_DOMAIN, Ad_Page
import settings

# String used to define a browser when making DART requests from a commandline
DEFAULT_BROWSER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0.1) Gecko/20100101 Firefox/8.0.1"


def dart_sync(zones=None, *args, **kwargs):
	""" 
	Loops through all zones and positions and get's their status in doubleclick
	then updates the local database with the result.
	
	If zone value is passed, then it only loops through that custom list of zones
	"""
	if not zones:
		zones = Zone.objects.all()
		site_id = getattr(settings, "SITE_ID", None)
		if site_id:
			zones = zones.filter(site__site=site_id)

	for zone in zones:
		positions = zone.zone_position_set.all()
		for position in positions:
		
			size = position.position.size_list
			pos = position.position.slug
			ad_page = Ad_Page(zone=zone.slug, *args, **kwargs)	
			url = ad_page.js_url(pos, with_ord=True, size=size) 
			
			res = dart_request(url, *args, **kwargs)

			if res.status == 200:
				response = res.read()

				# if dart returns a blank image or document.write("");, there is no ad available, update its status				
				if re.search(r"grey\.gif", response) or response.strip() == "document.write("");":
					position.enabled = False
					#if settings.DEBUG: print "Position: disabled"
				else:
					position.enabled = True
					#if settings.DEBUG: print "Position: enabled"
				position.save()
				
def dart_request(url, user_agent=DEFAULT_BROWSER_AGENT, domain=DART_DOMAIN, *args, **kwargs):
	""" 
	Makes a single HTTP request of a DART tag to DART 
	server mimicking a browser request 
	"""
	conn = httplib.HTTPConnection(domain)
	conn.request(
		"GET",
		url,
		headers={
			"Referer": settings.SITE_URL, 
			"User-Agent": user_agent
		}
	)
	return conn.getresponse()
	