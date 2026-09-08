import os
import sys
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.checks import Error, Warning  # noqa: A004
from django.core.exceptions import ImproperlyConfigured
from django.core.management import color_style

from .blinding import get_unblinded_users, trial_is_blinded
from .site_randomizers import site_randomizers


@dataclass(frozen=True)
class Err:
    id: str
    cls: type[Warning | Error]


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


skip_verify_argv = (
    "tox",
    "test",
    "runtests.py",
    "showmigrations",
    "makemigrations",
    "migrate",
    "shell",
)


def running_management_command_or_tests() -> bool:
    """Return True if this process is a test run or one of the
    management commands that must not verify the list.

    Compares on the basename of each argv item. `sys.argv[0]` is the
    script exactly as it was typed, so an invocation such as
    `./runtests.py` or one giving an absolute path would otherwise not
    match and verification would run where it should be skipped.
    """
    argv = {Path(arg).name for arg in sys.argv}
    return any(name in argv for name in skip_verify_argv)


def randomizationlist_check(app_configs, **kwargs) -> list:
    sys.stdout.write(style.SQL_KEYWORD("randomizationlist_check ... \r"))
    errors = []
    error = error_configs.get("randomization_list_check")

    for randomizer in site_randomizers.registry.values():
        if kwargs.get("force_verify") or not running_management_command_or_tests():
            error_msgs = randomizer.verify_list()
            for error_msg in error_msgs:
                errors.append(error.cls(error_msg, hint=None, obj=None, id=error.id))  # noqa: PERF401
        if not settings.DEBUG:
            if not randomizer.get_randomizationlist_path().is_relative_to(settings.ETC_DIR):
                errors.append(
                    Warning(
                        "Insecure configuration. Randomization list file must be "
                        "stored in the etc folder. See settings.ETC_DIR. Got "
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
