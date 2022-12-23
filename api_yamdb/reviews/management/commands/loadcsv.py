"""Management-команда. Заполняет БД данными из csv-файлов.
Синтаксис:
python manage.py loadcsv csv_path model_name
"""
import pyfiglet
from csv import DictReader
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

app_models = [model.__name__ for model in apps.get_models()]
rename_csv_fields = {'category': 'category_id', 'author': 'author_id'}


class Command(BaseCommand):
    help = 'Заполняет базу данных модели из файла csv.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к файлу csv.')
        parser.add_argument('model_name', type=str, help='Имя модели.')

    def handle(self, *args, **options):
        if options['model_name'] not in app_models:
            raise CommandError(
                f'Модели "{options["model_name"]}" нет в приложении.')
        model = apps.get_model(app_label='reviews',
                               model_name=options['model_name'])

        try:
            incoming_data = DictReader(
                open(options['csv_path'], 'r', encoding="utf-8-sig"))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Файл не найден или некорректный путь {options["csv_path"]}')

        try:
            model.objects.bulk_create([
                model(
                    **{
                        rename_csv_fields.get(key) if rename_csv_fields.
                        get(key) else key: value
                        for key, value in row.items()
                    }) for row in incoming_data
            ])
        except Exception as error:
            presult = pyfiglet.figlet_format("Error", font="slant")
            raise self.stdout.write(
                self.style.ERROR(
                    f'Возникла ошибка при импорте данных в модель: {error}'
                    '\n======================================================='
                    f'\n{presult}'
                    '========================================================='
                ))
        presult = pyfiglet.figlet_format("Success", font="slant")
        self.stdout.write(
            self.style.SUCCESS(
                f'Данные из {options["csv_path"].split("/")[2]} '
                f'были успешно загружены в модель {options["model_name"]}'
                '\n==========================================================='
                f'\n{presult}'
                '============================================================='
            ))
