import os
import sys
from collections import namedtuple

from django.conf import settings
from django.core.checks import Warning
from django.core.management import color_style

from .site_randomizers import site_randomizers

err = namedtuple("Err", "id cls")

error_configs = dict(randomization_list_check=err("edc_randomization.W001", Warning))

style = color_style()


def randomizationlist_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("randomizationlist_check ... \r"))
    errors = []
    error = error_configs.get("randomization_list_check")

    for randomizer in site_randomizers.registry.values():
        if kwargs.get("force_verify") or (
            "tox" not in sys.argv
            and "test" not in sys.argv
            and "runtests.py" not in sys.argv
            and "showmigrations" not in sys.argv
            and "makemigrations" not in sys.argv
            and "migrate" not in sys.argv
            and "shell" not in sys.argv
        ):
            error_msgs = randomizer.verify_list()
            for error_msg in error_msgs:
                errors.append(error.cls(error_msg, hint=None, obj=None, id=error.id))
        if not settings.DEBUG:
            if settings.ETC_DIR not in randomizer.randomizationlist_path():
                errors.append(
                    Warning(
                        "Insecure configuration. Randomization list file must be "
                        "stored in the etc folder. Got "
                        f"{randomizer.randomizationlist_path()}",
                        hint="randomizationlist_path",
                        id="1000",
                    )
                )
            if os.access(randomizer.randomizationlist_path(), os.W_OK):
                errors.append(
                    Warning(
                        "Insecure configuration. File is writeable by this user. "
                        f"Got {randomizer.randomizationlist_path()}",
                        hint="randomizationlist_path",
                        id="1001",
                    )
                )
    sys.stdout.write(style.SQL_KEYWORD("randomization_list_check ... done.\n"))
    return errors
