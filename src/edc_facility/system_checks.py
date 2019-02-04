import os
import sys

from django.core.checks import Warning
from django.conf import settings


def holiday_check(app_configs, **kwargs):
    from .models import Holiday

    errors = []
    holiday_path = None

    try:
        holiday_path = settings.HOLIDAY_FILE
    except AttributeError:
        path_exists = False
    else:
        try:
            path_exists = os.path.exists(holiday_path)
        except TypeError:
            path_exists = False

    if not holiday_path:
        errors.append(
            Warning(
                "Holiday file not found! settings.HOLIDAY_FILE not defined. \n",
                id="edc_facility.001",
            )
        )
    elif not path_exists:
        errors.append(
            Warning(
                f"Holiday file not found! settings.HOLIDAY_FILE={holiday_path}. \n",
                id="edc_facility.002",
            )
        )

    if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
        if Holiday.objects.all().count() == 0:
            errors.append(
                Warning(
                    "Holiday table is empty. Run management command 'import_holidays'. "
                    "See edc_facility.Holidays",
                    id="edc_facility.003",
                )
            )
        else:
            if Holiday.objects.filter(country=settings.COUNTRY).count() == 0:
                countries = [obj.country for obj in Holiday.objects.all()]
                countries = list(set(countries))
                errors.append(
                    Warning(
                        f"No Holidays have been defined for this country. "
                        f"See edc_facility.Holidays. Expected one of {countries}. "
                        f"Got settings.COUNTRY="
                        f"'{settings.COUNTRY}'",
                        id="edc_facility.004",
                    )
                )
    return errors
