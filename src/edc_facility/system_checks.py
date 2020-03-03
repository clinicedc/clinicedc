import csv
import os

from django.conf import settings
from django.core.checks import Warning


def holiday_path_check(app_configs, **kwargs):
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


def holiday_country_check(app_configs, **kwargs):
    errors = []
    holiday_path = settings.HOLIDAY_FILE

    country = getattr(settings, "COUNTRY", None)
    if not country:
        errors.append(
            Warning(
                f"Holiday file has no records for current country! "
                f"See settings.COUNTRY. Got None\n",
                id="edc_facility.003",
            )
        )
    else:
        with open(holiday_path, "r") as f:
            reader = csv.DictReader(f, fieldnames=["local_date", "label", "country"])
            if not [row["country"] for row in reader if row["country"] == country]:
                errors.append(
                    Warning(
                        f"Holiday file has no records for current country! "
                        f"See settings.COUNTRY. Got {country}\n",
                        id="edc_facility.004",
                    )
                )
    return errors
