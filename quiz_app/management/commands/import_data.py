import csv
from django.core.management.base import BaseCommand
from quiz_app.models import Species, Region, Month, SpeciesAreaWeight, SpeciesPeriodWeight
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def handle(self, *args, **options):
        self.import_species()
        self.import_regions()
        self.import_months()
        self.import_species_area_weights()
        self.import_species_period_weights()

    def import_species(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'species.csv')
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Species.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'family': row['family'],
                        'probability': float(row['probability'])
                    }
                )

    def import_regions(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'species_area_weights.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for region_name in headers[1:]:
                Region.objects.get_or_create(name=region_name)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {Region.objects.count()} regions'))

    def import_months(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'species_period_weights.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for month_name in headers[1:]:
                Month.objects.get_or_create(name=month_name)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {Month.objects.count()} months'))

    def import_species_area_weights(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'species_area_weights.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            regions = {name: Region.objects.get(name=name) for name in headers[1:]}
            weights_created = 0
            for row in reader:
                species, _ = Species.objects.get_or_create(name=row[0])
                for i, weight in enumerate(row[1:], 1):
                    if weight.strip():  # Check if weight is not empty
                        region = regions[headers[i]]
                        SpeciesAreaWeight.objects.update_or_create(
                            species=species,
                            region=region,
                            defaults={'weight': float(weight)}
                        )
                        weights_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {weights_created} species area weights'))

    def import_species_period_weights(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'species_period_weights.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            months = {name: Month.objects.get(name=name) for name in headers[1:]}
            weights_created = 0
            for row in reader:
                species, _ = Species.objects.get_or_create(name=row[0])
                for i, weight in enumerate(row[1:], 1):
                    if weight.strip():  # Check if weight is not empty
                        month = months[headers[i]]
                        SpeciesPeriodWeight.objects.update_or_create(
                            species=species,
                            month=month,
                            defaults={'weight': float(weight)}
                        )
                        weights_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {weights_created} species period weights'))