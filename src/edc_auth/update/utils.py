import sys

from copy import copy
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pprint import pprint
from warnings import warn

from ..codename_tuples import navbar_tuples, dashboard_tuples, rando_tuples

INVALID_APP_LABEL = "invalid_app_label"


class PermissionsCodenameError(Exception):
    pass


class PermissionsCreatorError(ValidationError):
    pass


class CodenameDoesNotExist(Exception):
    pass


def get_from_codename_tuple(codename_tpl, app_label=None):
    try:
        value, name = codename_tpl
    except ValueError as e:
        raise ValueError(f"{e} Got {codename_tpl}")
    _app_label, codename = value.split(".")
    if app_label and _app_label != app_label:
        raise PermissionsCreatorError(
            f"app_label in permission codename does not match. "
            f"Expected {app_label}. Got {_app_label}. "
            f"See {codename_tpl}.",
            code=INVALID_APP_LABEL,
        )
    return _app_label, codename, name


def create_permissions_from_tuples(model, codename_tpls):
    """Creates custom permissions on model "model".
    """
    if codename_tpls:
        try:
            model_cls = django_apps.get_model(model)
        except LookupError as e:
            warn(f"{e}. Got {model}")
        else:
            content_type = ContentType.objects.get_for_model(model_cls)
            for codename_tpl in codename_tpls:
                app_label, codename, name = get_from_codename_tuple(
                    codename_tpl, model_cls._meta.app_label
                )
                try:
                    Permission.objects.get(
                        codename=codename, content_type=content_type)
                except ObjectDoesNotExist:
                    Permission.objects.create(
                        name=name, codename=codename, content_type=content_type
                    )
                verify_codename_exists(f"{app_label}.{codename}")


def create_edc_dashboard_permissions(extra_codename_tpls=None):
    model = "edc_dashboard.dashboard"
    create_permissions_from_tuples(model, dashboard_tuples)
    create_permissions_from_tuples(model, extra_codename_tpls)
    for group in Group.objects.all():
        remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_dashboard.add_dashboard",
                "edc_dashboard.change_dashboard",
                "edc_dashboard.delete_dashboard",
                "edc_dashboard.view_dashboard",
            ],
        )


def create_rando_permissions():
    model = "edc_randomization.randomizationlist"
    create_permissions_from_tuples(model, rando_tuples)
    for group in Group.objects.all():
        remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_randomization.add_randomizationlist",
                "edc_randomization.change_randomizationlist",
                "edc_randomization.delete_randomizationlist",
            ],
        )


def create_edc_navbar_permissions(extra_codename_tpls=None):
    model = "edc_navbar.navbar"
    create_permissions_from_tuples(model, navbar_tuples)
    create_permissions_from_tuples(model, extra_codename_tpls)
    for group in Group.objects.all():
        remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_navbar.add_navbar",
                "edc_navbar.change_navbar",
                "edc_navbar.delete_navbar",
                "edc_navbar.view_navbar",
            ],
        )


def create_or_update_groups(group_names, verbose=None):
    """Add/Deletes group model instances to match the
    the given list of group names.
    """

    for name in group_names:
        try:
            Group.objects.get(name=name)
        except ObjectDoesNotExist:
            Group.objects.create(name=name)
    Group.objects.exclude(name__in=group_names).delete()

#     if verbose:
#         names = [obj.name for obj in Group.objects.all().order_by("name")]
#         sys.stdout.write(f"  Groups are: {', '.join(names)}\n")


def get_from_dotted_codename(codename=None, default_app_label=None, **kwargs):
    if not codename:
        raise PermissionsCodenameError(
            f"Invalid codename. May not be None. Opts={kwargs}."
        )
    try:
        app_label, _codename = codename.split(".")
    except ValueError as e:
        if not default_app_label:
            raise PermissionsCodenameError(
                f"Invalid dotted codename. {e} Got {codename}."
            )
        app_label = default_app_label
        _codename = codename
    else:
        try:
            django_apps.get_app_config(app_label)
        except LookupError:
            raise PermissionsCodenameError(
                f"Invalid app_label in codename. Expected format "
                f"'<app_label>.<some_codename>'. Got {codename}."
            )
    return app_label, _codename


def get_permissions_from_codenames(codenames):
    permissions = []
    for dotted_codename in codenames:
        try:
            app_label, codename = get_from_dotted_codename(dotted_codename)
        except PermissionsCodenameError as e:
            warn(str(e))
        else:
            try:
                permissions.append(
                    Permission.objects.get(
                        codename=codename, content_type__app_label=app_label
                    )
                )
            except ObjectDoesNotExist as e:
                raise ObjectDoesNotExist(
                    f"{e}. Got codename={codename},app_label={app_label}"
                )
    return permissions


def add_permissions_to_group_by_codenames(group=None, codenames=None):
    if codenames:
        permissions = get_permissions_from_codenames(codenames)
        for permission in permissions:
            group.permissions.add(permission)


def remove_permissions_by_codenames(group=None, codenames=None):
    permissions = get_permissions_from_codenames(codenames)
    for permission in permissions:
        group.permissions.remove(permission)


def verify_codename_exists(codename):
    app_label, codename = get_from_dotted_codename(codename)
    try:
        permission = Permission.objects.get(
            codename=codename, content_type__app_label=app_label
        )
    except ObjectDoesNotExist as e:
        raise CodenameDoesNotExist(f"{e} Got '{app_label}.{codename}'")
    except MultipleObjectsReturned as e:
        raise CodenameDoesNotExist(f"{e} Got '{app_label}.{codename}'")
    return permission


def remove_pii_permissions_from_group(group, extra_pii_models=None):
    default_pii_models = [
        settings.SUBJECT_CONSENT_MODEL,
        "edc_locator.subjectlocator",
        "edc_registration.registeredsubject",
    ]
    default_pii_models.extend(extra_pii_models or [])
    for model in default_pii_models:
        remove_permissions_by_model(group, model)
        remove_historical_group_permissions(group, model)


def remove_permissions_by_model(group=None, model=None):
    try:
        model_cls = django_apps.get_model(model)
    except LookupError as e:
        warn(f"{e}. Got {model}")
    else:
        content_type = ContentType.objects.get_for_model(model_cls)
        for permission in Permission.objects.filter(content_type=content_type):
            group.permissions.remove(permission)


def remove_historical_group_permissions(group=None, allowed_permissions=None):
    """Removes group permissions for historical models
    except those whose prefix is in `allowed_historical_permissions`.

    Default removes all except `view`.
    """
    allowed_permissions = allowed_permissions or ["view"]

    for action in allowed_permissions:
        for permission in group.permissions.filter(
            codename__contains="historical"
        ).exclude(codename__startswith=action):
            group.permissions.remove(permission)


def show_permissions_for_group(group_name=None):
    group = Group.objects.get(name=group_name)
    print(group.name)
    pprint([p for p in group.permissions.all()])


def remove_codenames_for_app_labels(codenames_by_group, excluded_app_labels=None):
    """Removes codenames that refer to app_labels that are not
    installed.

    excluded_app_labels: Explicitly list the app_labels to remove
    """
    if not excluded_app_labels:
        app_labels = []
        for codenames in codenames_by_group.values():
            for codename in codenames:
                app_label, _ = codename.split(".")
                app_labels.append(app_label)

        installed_app_labels = list(
            set([a.split(".")[0] for a in settings.INSTALLED_APPS])
        )
        excluded_app_labels = list(
            set(
                [
                    app_label
                    for app_label in app_labels
                    if app_label not in installed_app_labels
                ]
            )
        )
        excluded_app_labels.remove("auth")
        excluded_app_labels.remove("sites")
        excluded_app_labels.remove("admin")
        warn(
            f"Removing codenames for apps that are not installed. "
            f"Got {', '.join(excluded_app_labels)}. See edc_auth."
        )

    if excluded_app_labels:
        codenames_by_group_copy = {k: v for k, v in codenames_by_group.items()}
        for group_name, codenames in codenames_by_group_copy.items():
            original_codenames = copy(codenames)
            for codename in original_codenames:
                for app_label in excluded_app_labels:
                    if app_label in codename:
                        codenames.remove(codename)
            codenames_by_group[group_name] = codenames
    return codenames_by_group


def compare_codenames_for_group(group_name=None, expected=None):
    group = Group.objects.get(name=group_name)
    codenames = [p.codename for p in group.permissions.all()]

    new_expected = []
    for c in expected:
        try:
            c = c.split(".")[1]
        except IndexError:
            pass
        new_expected.append(c)

    compared = [c for c in new_expected if c not in codenames]
    if compared:
        print(group.name, "missing from codenames")
        pprint(compared)
    compared = [c for c in codenames if c not in new_expected]
    if compared:
        print(group.name, "extra codenames")
        pprint(compared)
