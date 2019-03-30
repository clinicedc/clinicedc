from django.apps import apps as django_apps


class PermissionsCodenameError(Exception):
    pass


def verify_permission_codename(permission_codename, **kwargs):
    permission_codename = (
        "edc_navbar.everyone" if permission_codename is None else permission_codename)
    try:
        app_label, codename = permission_codename.split(".")
    except ValueError:
        app_label = "edc_navbar"
        codename = permission_codename
    else:
        if app_label not in [a.name for a in django_apps.get_app_configs()]:
            raise PermissionsCodenameError(
                f"Invalid Navbar codename. Expected format "
                f"'<app_label>.<some_codename>'. Got {permission_codename}.")
    permission_codename = f"{app_label}.{codename}"
    return permission_codename
