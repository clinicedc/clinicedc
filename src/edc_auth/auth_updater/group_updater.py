import sys
from typing import Any, List, Optional
from warnings import warn

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.management.color import color_style

from ..auth_objects import PII, PII_VIEW

style = color_style()

INVALID_APP_LABEL = "invalid_app_label"


class PermissionsCodenameError(Exception):
    pass


class PermissionsCreatorError(ValidationError):
    pass


class CodenameDoesNotExist(Exception):
    pass


class GroupUpdater:
    def __init__(
        self,
        groups: Optional[dict] = None,
        apps=None,
        verbose=None,
        pii_models: Optional[list] = None,
        custom_permissions_tuples: Optional[dict] = None,
        warn_only=None,
        codename_prefixes: Optional[list] = None,
    ):
        self.apps = apps or django_apps
        self.content_type_model_cls = self.apps.get_model("contenttypes.contenttype")
        self.custom_permissions_tuples = custom_permissions_tuples
        self.group_model_cls = self.apps.get_model("auth.group")
        self.group_names = list(groups.keys())
        self.groups = groups
        self.permission_model_cls = self.apps.get_model("auth.permission")
        self.pii_models = pii_models or []
        self.verbose = verbose
        self.warn_only = getattr(settings, "EDC_AUTH_CODENAMES_WARN_ONLY", warn_only)

        # TODO: perhaps change edc_navbar codenames to have a prefix such as `access`
        self.codename_prefixes = codename_prefixes or [
            "view",
            "add",
            "change",
            "delete",
            "import",
            "export",
            "nav",
            "display",
        ]

    def update_groups(self):
        if self.verbose:
            sys.stdout.write(style.MIGRATE_HEADING(" - Updating groups:\n"))
        for group_name, codenames in self.groups.items():
            self.update_group(group_name, codenames, create_group=True)
        for group in self.group_model_cls.objects.exclude(name__in=[PII, PII_VIEW]):
            self.remove_pii_permissions_from_group(group)
        self.group_model_cls.objects.exclude(name__in=self.group_names).delete()
        if self.verbose:
            sys.stdout.write("   Done.\n")

    def update_group(self, group_name, codenames, create_group=None):
        if self.verbose:
            sys.stdout.write(f"   * {group_name.lower()}\n")
        try:
            group = self.group_model_cls.objects.get(name=group_name)
        except ObjectDoesNotExist as e:
            if not create_group:
                raise ObjectDoesNotExist(f"{e} Got {group_name}")
            group = self.group_model_cls.objects.create(name=group_name)
        else:
            group.permissions.clear()
        self.add_permissions_to_group_by_codenames(group, codenames)
        self.remove_historical_group_permissions(group)

    def add_permissions_to_group_by_codenames(self, group=None, codenames=None):
        if codenames:
            permissions = self.get_permissions_qs_from_codenames(codenames)
            for permission in permissions:
                group.permissions.add(permission)

    def get_permissions_qs_from_codenames(
        self, codenames: List[Any], allow_multiple_objects: Optional[bool] = None
    ):
        """Returns a list of permission model instances for the given
        codenames.

        codenames:  a list of codenames or a list of functions that
                      returns a list. Combining codenames and funcs
                      in a list also works.
        """
        permissions = []
        expanded_codenames = []
        for item in codenames:
            try:
                expanded_codenames.extend(item())
            except TypeError:
                expanded_codenames.append(item)
        for dotted_codename in expanded_codenames:
            try:
                app_label, codename = self.get_from_dotted_codename(dotted_codename)
            except PermissionsCodenameError as e:
                warn(str(e))
            else:
                try:
                    permissions.append(
                        self.permission_model_cls.objects.get(
                            codename=codename, content_type__app_label=app_label
                        )
                    )
                except ObjectDoesNotExist as e:
                    errmsg = f"{e} Got codename={codename},app_label={app_label}"
                    if not self.warn_only:
                        raise CodenameDoesNotExist(errmsg)
                    warn(style.ERROR(errmsg))
                except MultipleObjectsReturned as e:
                    if not allow_multiple_objects:
                        raise MultipleObjectsReturned(
                            f"{str(e)} See `{app_label}.{codename}`."
                        )
                    permissions.extend(
                        [
                            obj
                            for obj in self.permission_model_cls.objects.filter(
                                codename=codename, content_type__app_label=app_label
                            )
                        ]
                    )
        return permissions

    def get_from_dotted_codename(self, codename=None):
        """Returns a tuple of app_label, codename.

        Validates the codename format, '<app_label>.<some_codename>',
        and the `app_label` in a given codename.
        """
        if not codename:
            raise PermissionsCodenameError("Invalid codename. May not be None.")
        try:
            app_label, _codename = codename.split(".")
        except ValueError as e:
            raise PermissionsCodenameError(f"Invalid dotted codename. {e} Got {codename}.")
        else:
            try:
                self.apps.get_app_config(app_label)
            except LookupError:
                raise PermissionsCodenameError(
                    "Invalid app_label in codename. Expected format "
                    f"'<app_label>.<some_codename>'. Got {codename}."
                )
        prefix = _codename.split("_")[0]
        if prefix not in self.codename_prefixes:
            raise PermissionsCodenameError(
                f"Invalid codename prefix. Expected one of {self.codename_prefixes}. "
                f"Got {_codename}."
            )
        return app_label, _codename

    def remove_pii_permissions_from_group(self, group):
        for model in self.pii_models:
            self.remove_permissions_by_model(group, model)

    @staticmethod
    def remove_historical_group_permissions(group=None, model=None):
        """Removes permissions for historical models from this
        group.

        Default removes all except `view`.
        """

        opts = dict(codename__contains="_historical")
        if model:
            opts.update(model=model)
        for permission in group.permissions.filter(**opts).exclude(
            codename__startswith="view_historical"
        ):
            group.permissions.remove(permission)

    def remove_permissions_by_model(self, group=None, model=None):
        try:
            model_cls = self.apps.get_model(model)
        except LookupError as e:
            warn(f"Unable to remove permissions. {e}. Got {model}")
        else:
            content_type = self.content_type_model_cls.objects.get_for_model(model_cls)
            for permission in self.permission_model_cls.objects.filter(
                content_type=content_type
            ):
                group.permissions.remove(permission)

    def create_custom_permissions_from_tuples(self):
        for model, codename_tuples in self.custom_permissions_tuples.items():
            self.create_permissions_from_tuples(model, codename_tuples)

    def create_permissions_from_tuples(self, model=None, codename_tuples=None):
        """Creates custom permissions on model `model`."""
        if codename_tuples:
            try:
                model_cls = self.apps.get_model(model)
            except LookupError as e:
                warn(f"{e}. Got {model}")
            else:
                content_type = self.content_type_model_cls.objects.get_for_model(model_cls)
                for codename_tpl in codename_tuples:
                    app_label, codename, name = self.get_from_codename_tuple(
                        codename_tpl, model_cls._meta.app_label
                    )
                    try:
                        self.permission_model_cls.objects.get(
                            codename=codename, content_type=content_type
                        )
                    except ObjectDoesNotExist:
                        self.permission_model_cls.objects.create(
                            name=name, codename=codename, content_type=content_type
                        )
                    self.verify_codename_exists(f"{app_label}.{codename}")

    def verify_codename_exists(self, codename):
        app_label, codename = self.get_from_dotted_codename(codename)
        try:
            permission = self.permission_model_cls.objects.get(
                codename=codename, content_type__app_label=app_label
            )
        except ObjectDoesNotExist as e:
            raise CodenameDoesNotExist(f"{e} Got '{app_label}.{codename}'")
        except MultipleObjectsReturned as e:
            raise CodenameDoesNotExist(f"{e} Got '{app_label}.{codename}'")
        return permission

    @staticmethod
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

    def remove_permissions_by_codenames(
        self, group=None, codenames=None, allow_multiple_objects: Optional[bool] = None
    ):
        """Remove the given codenames from the given group."""
        permissions = self.get_permissions_qs_from_codenames(
            codenames, allow_multiple_objects=allow_multiple_objects
        )
        for permission in permissions:
            group.permissions.remove(permission)
