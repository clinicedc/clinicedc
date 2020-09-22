import sys

from copy import copy, deepcopy
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
    MultipleObjectsReturned,
)
from django.core.management.color import color_style
from edc_auth.codename_tuples import navbar_tuples, get_rando_tuples
from edc_randomization.site_randomizers import site_randomizers
from warnings import warn

from .codename_tuples import dashboard_tuples
from .get_default_codenames_by_group import get_default_codenames_by_group
from .group_names import PII, PII_VIEW

INVALID_APP_LABEL = "invalid_app_label"
EDC_AUTH_CODENAMES_WARN_ONLY = getattr(settings, "EDC_AUTH_CODENAMES_WARN_ONLY", False)
style = color_style()
site_randomizers.autodiscover()


class PermissionsCodenameError(Exception):
    pass


class PermissionsCreatorError(ValidationError):
    pass


class CodenameDoesNotExist(Exception):
    pass


def get_app_label(a):
    a = a.split(".apps.")[0]
    return a.split(".")[-1]


class GroupPermissionsUpdater:
    def __init__(
        self,
        codenames_by_group=None,
        extra_pii_models=None,
        excluded_app_labels=None,
        create_codename_tuples=None,
        apps=None,
        verbose=None,
    ):
        self.apps = apps or django_apps
        self.verbose = verbose
        self.codenames_by_group = codenames_by_group or get_default_codenames_by_group()
        self._exclude_app_labels(excluded_app_labels)

        self.extra_pii_models = extra_pii_models or []
        self.create_codename_tuples = create_codename_tuples
        self.update_group_permissions()

    def update_group_permissions(self):
        """Update group permissions for each registered randomizer class."""
        if self.verbose:
            sys.stdout.write(
                style.MIGRATE_HEADING("Updating groups and permissions:\n")
            )
        self.create_or_update_groups()
        self.create_permissions_from_tuples(
            "edc_dashboard.dashboard", self.dashboard_tuples
        )
        self.create_permissions_from_tuples("edc_navbar.navbar", self.navbar_tuples)

        for model, codename_tuples in (self.create_codename_tuples or {}).items():
            self.create_permissions_from_tuples(model, codename_tuples)

        for randomizer_cls in site_randomizers._registry.values():
            if self.verbose:
                sys.stdout.write(
                    "  creating permissions for registered randomizer_cls "
                    f"`{randomizer_cls.name}` model "
                    f"`{randomizer_cls.model_cls()._meta.label_lower}`\n"
                )
            rando_tuples = [
                (k, v)
                for k, v in self.rando_tuples
                if k.startswith(
                    randomizer_cls.model_cls()._meta.label_lower.split(".")[0]
                )
            ]
            self.create_permissions_from_tuples(
                randomizer_cls.model_cls()._meta.label_lower, rando_tuples,
            )
        self.create_permissions_from_tuples("edc_navbar.navbar", self.navbar_tuples)
        self.remove_permissions_to_dummy_models()
        self.make_randomizationlist_view_only()

        self.update_codenames_by_group()

        if self.verbose:
            sys.stdout.write(style.MIGRATE_HEADING("Done\n"))
            sys.stdout.flush()

    def update_codenames_by_group(self):
        for group_name, codenames in self.codenames_by_group.items():
            if self.verbose:
                sys.stdout.write(f"  * {group_name.lower()}\n")
            try:
                group = self.group_model_cls.objects.get(name=group_name)
            except ObjectDoesNotExist as e:
                raise ObjectDoesNotExist(f"{e} Got {group_name}")

            group.permissions.clear()
            self.add_permissions_to_group_by_codenames(group, codenames)
            if group.name not in [PII, PII_VIEW]:
                self.remove_pii_permissions_from_group(group)
            self.remove_historical_group_permissions(group)

    @property
    def dashboard_tuples(self):
        return dashboard_tuples

    @property
    def navbar_tuples(self):
        return navbar_tuples

    @property
    def rando_tuples(self):
        return get_rando_tuples()

    @property
    def group_model_cls(self):
        return self.apps.get_model("auth.group")

    @property
    def content_type_model_cls(self):
        return self.apps.get_model("contenttypes.contenttype")

    @property
    def group_names(self):
        return list(self.codenames_by_group.keys())

    @property
    def permission_model_cls(self):
        return self.apps.get_model("auth.permission")

    def _exclude_app_labels(self, excluded_app_labels=None):
        """
        Removes codenames that refer to excluded app_labels. (for tests)
        """
        if excluded_app_labels:
            dct_copy = deepcopy(self.codenames_by_group)
            for group_name, codenames in dct_copy.items():
                original_codenames = copy(codenames)
                for codename in original_codenames:
                    for app_label in excluded_app_labels:
                        if app_label == codename.split(".")[0]:
                            codenames.remove(codename)
                self.codenames_by_group[group_name] = codenames

    def create_or_update_groups(self):
        """Add/Deletes group model instances to match the
        the list of group names.
        """
        for name in self.group_names:
            try:
                self.group_model_cls.objects.get(name=name)
            except ObjectDoesNotExist:
                self.group_model_cls.objects.create(name=name)
        self.group_model_cls.objects.exclude(name__in=self.group_names).delete()

    def make_randomizationlist_view_only(self):
        for randomizer_cls in site_randomizers._registry.values():
            app_label, model = randomizer_cls.model_cls(
                apps=self.apps
            )._meta.label_lower.split(".")
            permissions = self.permission_model_cls.objects.filter(
                content_type__app_label=app_label, content_type__model=model
            ).exclude(codename=f"view_{model}")
            codenames = [f"{app_label}.{o.codename}" for o in permissions]
            codenames.extend(
                [
                    f"{app_label}.add_{model}",
                    f"{app_label}.change_{model}",
                    f"{app_label}.delete_{model}",
                ]
            )
            codenames = list(set(codenames))
            for group in self.group_model_cls.objects.all():
                self.remove_permissions_by_codenames(
                    group=group, codenames=codenames,
                )

    def remove_permissions_to_dummy_models(self):
        for group in self.group_model_cls.objects.all():
            self.remove_permissions_by_codenames(
                group=group,
                codenames=[
                    "edc_dashboard.add_dashboard",
                    "edc_dashboard.change_dashboard",
                    "edc_dashboard.delete_dashboard",
                    "edc_dashboard.view_dashboard",
                    "edc_navbar.add_navbar",
                    "edc_navbar.change_navbar",
                    "edc_navbar.delete_navbar",
                    "edc_navbar.view_navbar",
                ],
            )

    def create_permissions_from_tuples(self, model=None, codename_tuples=None):
        """Creates custom permissions on model "model".
        """
        if codename_tuples:
            try:
                model_cls = self.apps.get_model(model)
            except LookupError as e:
                warn(f"{e}. Got {model}")
            else:
                content_type = self.content_type_model_cls.objects.get_for_model(
                    model_cls
                )
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

    def remove_permissions_by_codenames(self, group=None, codenames=None):
        """Remove the given codenames from the given group.
        """
        permissions = self.get_permissions_qs_from_codenames(codenames)
        for permission in permissions:
            group.permissions.remove(permission)

    def get_permissions_qs_from_codenames(self, codenames):
        """Returns a list of permission model instances for the given
        codenames.
        """
        permissions = []
        for dotted_codename in codenames:
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
                    errmsg = f"{e}. Got codename={codename},app_label={app_label}"
                    if EDC_AUTH_CODENAMES_WARN_ONLY:
                        warn(style.ERROR(errmsg))
                    else:
                        raise ObjectDoesNotExist(errmsg)
                except MultipleObjectsReturned as e:
                    raise MultipleObjectsReturned(
                        f"{str(e)} See `{app_label}.{codename}`."
                    )
        return permissions

    def get_from_dotted_codename(self, codename=None):
        """Returns a tuple of app_label, codename.

        Validates given codename.
        """
        if not codename:
            raise PermissionsCodenameError("Invalid codename. May not be None.")
        try:
            app_label, _codename = codename.split(".")
        except ValueError as e:
            raise PermissionsCodenameError(
                f"Invalid dotted codename. {e} Got {codename}."
            )
        else:
            try:
                self.apps.get_app_config(app_label)
            except LookupError:
                raise PermissionsCodenameError(
                    f"Invalid app_label in codename. Expected format "
                    f"'<app_label>.<some_codename>'. Got {codename}."
                )
        return app_label, _codename

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

    def add_permissions_to_group_by_codenames(self, group=None, codenames=None):
        if codenames:
            permissions = self.get_permissions_qs_from_codenames(codenames)
            for permission in permissions:
                group.permissions.add(permission)

    def remove_pii_permissions_from_group(self, group):
        default_pii_models = [
            settings.SUBJECT_CONSENT_MODEL,
            "edc_locator.subjectlocator",
            "edc_registration.registeredsubject",
        ]
        default_pii_models.extend(self.extra_pii_models)
        for model in default_pii_models:
            self.remove_permissions_by_model(group, model)

    def remove_permissions_by_model(self, group=None, model=None):
        try:
            model_cls = self.apps.get_model(model)
        except LookupError as e:
            warn(f"{e}. Got {model}")
        else:
            content_type = self.content_type_model_cls.objects.get_for_model(model_cls)
            for permission in self.permission_model_cls.objects.filter(
                content_type=content_type
            ):
                group.permissions.remove(permission)

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
