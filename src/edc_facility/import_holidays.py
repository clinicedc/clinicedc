import csv
import os
import sys

from datetime import datetime
from django.apps import apps as django_apps
from django.conf import settings
from tqdm import tqdm


class HolidayImportError(Exception):
    pass


class HolidayFileNotFoundError(Exception):
    pass


def import_holidays(verbose=None):
    model_cls = django_apps.get_model('edc_facility.holiday')
    path = settings.HOLIDAY_FILE
    try:
        if not os.path.exists(path):
            raise HolidayFileNotFoundError(path)
    except TypeError:
        raise HolidayImportError(f'Invalid path. Got {path}.')
    if verbose:
        sys.stdout.write(
            f'\nImporting holidays from \'{path}\' '
            f'into {model_cls._meta.label_lower}\n')
    model_cls.objects.all().delete()

    recs = check_for_duplicates_in_file(path)

    import_file(path, recs, model_cls)

    if verbose:
        sys.stdout.write(f'Done.\n')


def check_for_duplicates_in_file(path):
    """Returns a list of records.
    """
    with open(path, 'r') as f:
        reader = csv.DictReader(
            f, fieldnames=['local_date', 'label', 'country'])
        recs = [(row['local_date'], row['country']) for row in reader]
    if len(recs) != len(list(set(recs))):
        raise HolidayImportError(
            'Invalid file. Duplicate dates detected for a country')
    return recs


def import_file(path, recs, model_cls):
    objs = []
    with open(path, 'r') as f:
        reader = csv.DictReader(
            f, fieldnames=['local_date', 'label', 'country'])
        for index, row in tqdm(enumerate(reader), total=len(recs)):
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
