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


def randomization_list_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("randomization_list_check ... \r"))
    errors = []
    error = error_configs.get("randomization_list_check")
    for randomizer in site_randomizers.registry.values():
        if (
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
            if settings.ETC_DIR not in randomizer.get_randomization_list_path():
                errors.append(
                    Warning(
                        "Insecure configuration. Randomization list file must be "
                        "stored in the etc folder. Got "
                        f"{randomizer.get_randomization_list_path()}",
                        id="randomization_list_path",
                    )
                )
            if os.access(randomizer.get_randomization_list_path(), os.W_OK):
                errors.append(
                    Warning(
                        "Insecure configuration. File is writeable by this user. "
                        f"Got {randomizer.get_randomization_list_path()}",
                        id="randomization_list_path",
                    )
                )
    sys.stdout.write(style.SQL_KEYWORD("randomization_list_check ... done.\n"))
    return errors
