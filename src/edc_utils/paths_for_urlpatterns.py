from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from django.urls.conf import include, path

if TYPE_CHECKING:
    from django.urls import URLPattern


def paths_for_urlpatterns(app_name) -> list[URLPattern]:
    paths: list[URLPattern] = []
    try:
        admin_site = import_module(f"{app_name}.admin_site")
    except ModuleNotFoundError:
        pass
    else:
        paths.append(path(f"{app_name}/admin/", getattr(admin_site, f"{app_name}_admin").urls))
    paths.append(path(f"{app_name}/", include(f"{app_name}.urls")))
    return paths
