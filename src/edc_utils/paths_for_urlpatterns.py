from importlib import import_module

from django.urls.conf import include, path


def paths_for_urlpatterns(app_name):
    paths = []
    try:
        admin_site = import_module(f"{app_name}.admin_site")
    except ModuleNotFoundError:
        pass
    else:
        paths.append(path(f"{app_name}/admin/", getattr(admin_site, f"{app_name}_admin").urls))
    paths.append(path(f"{app_name}/", include(f"{app_name}.urls")))
    return paths
