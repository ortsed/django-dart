from django.core.management.base import BaseCommand, CommandError
from dart.tasks import dart_request
from optparse import make_option
from urlparse import urlparse

class Command(BaseCommand):
	help = "Makes a URL request to DART and prints the resulting HTML.  Wrap URLs in quotation marks to ensure that semicolons are not mistaken for separate bash commands"

	
	def handle(self, *args, **kwargs):
	
		if len(args) == 0:
			raise CommandError("No arguments specified.  URL needed to make a DART request")
		
		parsed_url = urlparse(args[0])
		if parsed_url.netloc:
			kwargs["domain"] = parsed_url.netloc
		
		response = dart_request(parsed_url.geturl(), *args, **kwargs)
		
		self.stdout.write("\nDART server response: \n\n" + response.read() + "\n\n")
