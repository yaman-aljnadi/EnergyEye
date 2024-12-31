from django.core.management.base import BaseCommand
from ...utils import generate_license

class Command(BaseCommand):
    help = 'Generate a license with a specified max number of devices'

    def add_arguments(self, parser):
        parser.add_argument('max_devices', type=int, help='The maximum number of devices for this license')

    def handle(self, *args, **kwargs):
        max_devices = kwargs['max_devices']
        license_key = generate_license(max_devices)
        self.stdout.write(self.style.SUCCESS(f'License generated: {license_key}'))