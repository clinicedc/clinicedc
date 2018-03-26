import csv
import os

from datetime import datetime
from django.apps import apps as django_apps
from django.conf import settings


class HolidayImportError(Exception):
    pass


class HolidayFileNotFoundError(Exception):
    pass


def import_holidays():
    model_cls = django_apps.get_model('edc_facility.holiday')
    path = settings.HOLIDAY_FILE
    try:
        if not os.path.exists(path):
            raise HolidayFileNotFoundError(path)
    except TypeError:
        raise HolidayImportError(f'Invalid path. Got {path}.')
    model_cls.objects.all().delete()
    objs = []
    with open(path, 'r') as f:
        reader = csv.DictReader(
            f, fieldnames=['local_date', 'label', 'country'])
        for index, row in enumerate(reader):
            if index == 0:
                continue
            try:
                local_date = datetime.strptime(
                    row['local_date'], '%Y-%m-%d').date()
            except ValueError as e:
                raise HolidayImportError(
                    f'Invalid format when importing from '
                    f'{path}. Got \'{e}\'')
            else:
                objs.append(model_cls(
                    country=row['country'],
                    local_date=local_date,
                    name=row['label']))
        model_cls.objects.bulk_create(objs)
