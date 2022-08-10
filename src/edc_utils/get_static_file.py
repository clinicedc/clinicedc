import os
from urllib.error import URLError
from urllib.request import urlretrieve

from django.conf import settings


def get_static_file(app_label: str, filename: str) -> str:
    path = os.path.join(settings.STATIC_ROOT or "", app_label, filename)
    if os.path.isfile(path):
        try:
            with open(path, "r"):
                pass
        except FileNotFoundError:
            path = os.path.join(f"https://{settings.STATIC_URL}", app_label, filename)
            try:
                urlretrieve(path)  # nosec B310
            except URLError:
                raise FileNotFoundError(
                    f"Static file not found. Tried "
                    f"STATIC_ROOT ({settings.STATIC_ROOT}) and "
                    f"STATIC_URL ({settings.STATIC_URL}). "
                    f"Got {app_label}/{filename}."
                )
    return path
