import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'loading ingredients from data in json'

    def handle(self, *args, **options):
        try:
            file_name = 'recipes/data/ingredients.csv'
            with open(file_name, 'r',
                      encoding='utf-8') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    name, measurement_unit = row
                    try:
                        Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    except IntegrityError:
                        print(f'Ингредиент {name} {measurement_unit} '
                              f'уже есть в базе')
            print(f'Данные из {file_name} загружены')
            file_name = 'recipes/data/tags.csv'
            with open(file_name, 'r',
                      encoding='utf-8') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    name, color, slug = row
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )
            print(f'Данные из {file_name} загружены')
        except FileNotFoundError:
            raise CommandError(f'{file_name} отсутствует в директории data')
