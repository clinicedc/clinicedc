import os

from django.apps import apps as django_apps
from django.conf import settings
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist


class EdcTemplateDoesNotExist(Exception):
    pass


def insert_bootstrap_version(**template_data):
    """Returns template data after inserting bootstrap version
    in each path, if not already inserted.
    """

    try:
        bootstrap_version = settings.EDC_BOOTSTRAP
    except AttributeError:
        bootstrap_version = 3
    if bootstrap_version:
        for key, original_path in template_data.items():
            try:
                get_template(original_path)
            except TemplateDoesNotExist:
                if "bootstrap" not in original_path:
                    path = get_template_path_with_bootstrap(
                        original_path, bootstrap_version
                    )
                    template_data.update({key: path})
    return template_data


def get_template_path_with_bootstrap(original_path, bootstrap_version):
    """Returns a new path with the bootstrap version inserted
    or raises EdcTemplateDoesNotExist.
    """
    for app_config in django_apps.get_app_configs():
        if app_config.name in original_path:
            app_name = app_config.name
            break
    if not app_name:
        raise EdcTemplateDoesNotExist(
            f"Template file path refers to unknown app_name. "
            f"Is the app listed in INSTALLED_APPS? "
            f"Is the app_config.name correctly loaded and set? "
            f"Got {original_path}"
        )
    else:
        path_list = splitall(original_path)
        path_list.insert(1, f"bootstrap{bootstrap_version}")
        path = os.path.join(*path_list)
        try:
            get_template(path)
        except TemplateDoesNotExist as e:
            raise EdcTemplateDoesNotExist(
                f"Template file does not exist. "
                f"Tried {original_path} and {path}. Got {e}"
            )
    return path


def splitall(path):
    """Taken from
    https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
