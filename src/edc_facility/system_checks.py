import os

from django.conf import settings
from django.core.checks import Warning


def holiday_check(app_configs, **kwargs):

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
    return errors
