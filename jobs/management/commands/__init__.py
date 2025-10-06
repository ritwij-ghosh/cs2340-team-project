from django.core.management.base import BaseCommand
from jobs.utils import geocode_job_locations


class Command(BaseCommand):
    help = 'Geocode all jobs that don\'t have coordinates yet'

    def handle(self, *args, **options):
        self.stdout.write('Starting to geocode job locations...')
        
        try:
            geocoded_count = geocode_job_locations()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully geocoded {geocoded_count} jobs')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during geocoding: {str(e)}')
            )
