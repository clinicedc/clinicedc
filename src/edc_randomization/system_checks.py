import os
import sys
from dataclasses import dataclass
from typing import Type

from django.conf import settings
from django.core.checks import Error, Warning
from django.core.exceptions import ImproperlyConfigured
from django.core.management import color_style

from .blinding import get_unblinded_users, trial_is_blinded
from .site_randomizers import site_randomizers


@dataclass(frozen=True)
class Err:
    id: str
    cls: Type[Warning | Error]


error_configs = dict(
    randomization_list_check=Err("edc_randomization.W001", Warning),
    blinded_trial_settings_check=Err("edc_randomization.E002", Error),
)

style = color_style()


def blinded_trial_settings_check(app_configs, **kwargs) -> list:
    errors = []
    error = error_configs.get("blinded_trial_settings_check")
    if not trial_is_blinded():
        try:
            get_unblinded_users()
        except ImproperlyConfigured:
            error_msg = (
                "Trial is not a blinded trial but users are listed as unblinded. "
                "See EDC_RANDOMIZATION_UNBLINDED_USERS"
            )
            errors.append(error.cls(error_msg, hint=None, obj=None, id=error.id))
    return errors


def randomizationlist_check(app_configs, **kwargs) -> list:
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
            if not randomizer.get_randomizationlist_path().is_relative_to(settings.ETC_DIR):
                errors.append(
                    Warning(
                        "Insecure configuration. Randomization list file must be "
                        "stored in the etc folder. Got "
                        f"{randomizer.get_randomizationlist_path()}",
                        hint="randomizationlist_path",
                        id="1000",
                    )
                )
            if os.access(str(randomizer.get_randomizationlist_path()), os.W_OK):
                errors.append(
                    Warning(
                        "Insecure configuration. File is writeable by this user. "
                        f"Got {randomizer.get_randomizationlist_path()}",
                        hint="randomizationlist_path",
                        id="1001",
                    )
                )
    sys.stdout.write(style.SQL_KEYWORD("randomization_list_check ... done.\n"))
    return errors
