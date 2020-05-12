import csv
import os
import sys

from django.conf import settings
from django.core.checks import Warning
from django.core.management import color_style
from edc_sites import get_current_country

style = color_style()


def holiday_path_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("holiday_path_check ... \r"))
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
    sys.stdout.write(style.SQL_KEYWORD("holiday_path_check ... done.\n"))
    return errors


def holiday_country_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("holiday_country_check ... \r"))
    errors = []
    holiday_path = settings.HOLIDAY_FILE
    country = get_current_country()
    if country:
        with open(holiday_path, "r") as f:
            reader = csv.DictReader(f, fieldnames=["local_date", "label", "country"])
            if not [row["country"] for row in reader if row["country"] == country]:
                errors.append(
                    Warning(
                        f"Holiday file has no records for current country! "
                        f"See country in EdcSites definitions. Got {country}\n",
                        id="edc_facility.004",
                    )
                )
    sys.stdout.write(style.SQL_KEYWORD("holiday_country_check ... done.\n"))
    return errors
