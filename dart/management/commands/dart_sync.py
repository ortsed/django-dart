from django.core.management.base import BaseCommand, CommandError
from dart.tasks import dart_sync
from optparse import make_option

class Command(BaseCommand):
	help = "Syncs all zone-positions in DART app with their status in DART"
	
	option_list = BaseCommand.option_list + (
		make_option('--debug', default=False, action='store_true', dest='debug_mode', help='''
		Turn debug mode on, prints out synced URLs and their result to output
		'''),
		)
		
	def handle(self, *args, **kwargs):
		
		if dart_sync(*args, **kwargs):
			self.stdout.write("Successfully synced with DART server")
