import os

from django.conf import settings
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist


class EdcTemplateDoesNotExist(Exception):
    pass


def insert_bootstrap_version(**template_data):
    """Insert bootstrap version.
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
                if "/bootstrap" not in original_path:
                    base_name = os.path.basename(original_path)
                    prefix = original_path.split(base_name)[0]
                    path = os.path.join(
                        prefix, f"bootstrap{bootstrap_version}", base_name
                    )
                    try:
                        get_template(path)
                    except TemplateDoesNotExist as e:
                        raise EdcTemplateDoesNotExist(
                            f"Template file does not exist. "
                            f"Tried {original_path} and {path}. Got {e}"
                        )
                template_data.update({key: path})
    return template_data
