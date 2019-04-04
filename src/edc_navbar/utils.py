from django.apps import apps as django_apps


class PermissionsCodenameError(Exception):
    pass


def verify_permission_codename(
    permission_codename=None, default_app_label=None, **kwargs
):
    if not permission_codename:
        raise PermissionsCodenameError(
            f"Invalid codename. May not be None. Opts={kwargs}."
        )
    try:
        app_label, codename = permission_codename.split(".")
    except ValueError:
        app_label = default_app_label
        codename = permission_codename
    else:
        if app_label not in [a.name for a in django_apps.get_app_configs()]:
            raise PermissionsCodenameError(
                f"Invalid app_label in codename. Expected format "
                f"'<app_label>.<some_codename>'. Got {permission_codename}."
            )
    return app_label, codename
