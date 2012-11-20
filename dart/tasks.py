import httplib, re
from django.conf import settings
from dart.models import Zone, DART_DOMAIN, Ad_Page




def dart_sync(zones=None, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0.1) Gecko/20100101 Firefox/8.0.1", *args, **kwargs):
	""" 
	Loops through all zones and positions and get's their status in doubleclick
	then updates the local database with the result.
	
	If zones value is passed, then it only loops through that custom list of zones
	"""
	if not zones:
		zones = Zone.objects.all()
	
	for zone in zones:
		positions = zone.zone_position_set.all()
		for position in positions:
			conn = httplib.HTTPConnection(DART_DOMAIN)
			size = position.position.size_list
			pos = position.position.slug
			zone = zone.slug 
			ad_page = Ad_Page(zone=zone, *args, **kwargs)
			
			url = ad_page.js_url(pos, with_ord=True, size=size) 

			# HTTP request of a DART tag to DART server falsifying a browser request
			conn.request(
				"GET",
				url,
				headers={
					"Referer": settings.SITE_URL, 
					"User-Agent": user_agent
				}
			)
			
			
			res = conn.getresponse()
			if res.status == 200:
				response = res.read()

				# if dart returns a blank image or document.write("");, there is no ad available, update its status				
				if re.search(r"grey\.gif", response) or response.strip() == "document.write("");":
					position.enabled = False
				else:
					position.enabled = True
					
				position.save()