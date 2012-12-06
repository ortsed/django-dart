from django.core.management.base import BaseCommand, CommandError
from dart.tasks import dart_sync
from optparse import make_option

class Command(BaseCommand):
	help = "Syncs all zone-positions in DART app with their status in DART"
	
	def handle(self, *args, **kwargs):
		if dart_sync(*args, **kwargs):
			self.stdout.write("Successfully synced with DART server")
