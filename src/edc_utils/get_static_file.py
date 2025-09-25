from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlretrieve

from django.conf import settings


def get_static_file(app_label: str, filename: str) -> str:
    path = Path(settings.STATIC_ROOT or "") / app_label / filename
    # path as os path
    if path.is_file():
        try:
            with path.open("r"):
                pass
        except FileNotFoundError:
            path = None
    else:
        path = None

    # path as a url
    if not path:
        path = urljoin(f"https://{settings.STATIC_URL}", app_label, filename)
        try:
            urlretrieve(path)  # noqa: S310
        except URLError:
            path = None
    if not path:
        raise FileNotFoundError(
            f"Static file not found. Tried "
            f"STATIC_ROOT ({settings.STATIC_ROOT}) and "
            f"STATIC_URL ({settings.STATIC_URL}). "
            f"Got {app_label}/{filename}."
        )
    return path
