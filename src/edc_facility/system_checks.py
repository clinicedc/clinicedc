import csv
import sys
from pathlib import Path

from django.conf import settings
from django.core.checks import Error, Warning
from django.core.management import color_style
from edc_sites.site import sites

style = color_style()


def holiday_path_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("holiday_path_check ... \r"))
    errors = []
    if not getattr(settings, "HOLIDAY_FILE", None):
        errors.append(
            Error(
                "Holiday file path not set! See settings.HOLIDAY_FILE.\n",
                id="edc_facility.001",
            )
        )
    else:
        holiday_path = Path(settings.HOLIDAY_FILE).expanduser()
        if not holiday_path.exists():
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
    holiday_path = Path(settings.HOLIDAY_FILE).expanduser()
    if not sites.all():
        errors.append(Error("No sites have been registered", id="edc_facility.005"))
    else:
        with holiday_path.open(mode="r") as f:
            reader = csv.DictReader(f, fieldnames=["local_date", "label", "country"])
            next(reader, None)
            for row in reader:
                if row["country"] not in sites.countries:
                    errors.append(
                        Warning(
                            "Holiday file has no records for country! Sites are registered "
                            f"for these countries: `{'`, `'.join(sites.countries)}`. Got "
                            f"`{row['country']}`\n",
                            id="edc_facility.004",
                        )
                    )
                    break
    sys.stdout.write(style.SQL_KEYWORD("holiday_country_check ... done.\n"))
    return errors
