import os
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from edc_pdutils.model_to_dataframe import ModelToDataframe
from edc_utils import get_utcnow

from ..site_randomizers import site_randomizers


class RandomizationListExporterError(Exception):
    pass


def export_randomization_list(
    randomizer_name: str, path: Optional[str] = None, username: Optional[str] = None
):
    randomizer_cls = site_randomizers.get(randomizer_name)

    msg = (
        f"User `{username}` does not exist or does not have "
        f"permission to access '{randomizer_cls.model_cls()}'"
    )
    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        raise RandomizationListExporterError(msg)
    if not user.has_perms([randomizer_cls.model_cls()._meta.label_lower]):
        raise RandomizationListExporterError(msg)

    path = path or settings.EXPORT_FOLDER
    timestamp = get_utcnow().strftime("%Y%m%d%H%M")
    filename = os.path.expanduser(
        f"~/{settings.APP_NAME}_{randomizer_cls.name}_"
        f"randomizationlist_exported_{timestamp}.csv"
    )
    filename = os.path.join(path, filename)

    df = ModelToDataframe(
        model=randomizer_cls.model_cls()._meta.label_lower, decrypt=True, drop_sys_columns=True
    )
    opts = dict(
        path_or_buf=filename,
        encoding="utf-8",
        index=0,
        sep="|",
    )
    df.dataframe.to_csv(**opts)
    print(filename)
    return filename
