import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.admin import sites
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from django.db.models.fields import NOT_PROVIDED
from django.test.client import RequestFactory
from django.utils.safestring import mark_safe
from edc_list_data.model_mixins import ListModelMixin
from inspect import isfunction
from warnings import warn

from .models import DataDictionary, DataManagerUser


WIDGET = 1


class DbField:
    def __init__(self, model, fld):
        db_field = None
        try:
            db_field = model._meta.get_field(fld[0])
        except FieldDoesNotExist as e:
            warn(str(e))
        self.decimal_places = getattr(db_field, "decimal_places", None)
        self.default = self.get_default(db_field)
        self.field_name = getattr(db_field, "name", None)
        self.field_type = None if db_field is None else db_field.get_internal_type()
        self.help_text = mark_safe(getattr(db_field, "help_text", ""))
        self.max_digits = getattr(db_field, "max_digits", None)
        self.max_length = getattr(db_field, "max_length", None)
        self.nullable = getattr(db_field, "null", False)

    def get_default(self, db_field):
        default = getattr(db_field, "default", None)
        if default == NOT_PROVIDED:
            default = None
        if isfunction(default):
            default = default.__name__
        return default


def get_form_field_type(model, fld):
    field_type = None
    try:
        db_field = model._meta.get_field(fld[0])
    except FieldDoesNotExist as e:
        warn(str(e))
    else:
        field_type = db_field.get_internal_type()
    return field_type


def get_form_label(fld):
    try:
        label = str(fld[WIDGET].original_label)
    except AttributeError:
        label = str(fld[WIDGET].label)
    return label


def create_or_update_data_dictionary(index, model, fld):
    data_dictionary_model_cls = django_apps.get_model("edc_data_manager.datadictionary")
    label = get_form_label(fld)
    options = dict(
        active=True,
        model=model._meta.label_lower,
        number=index + 1,
        prompt=mark_safe(label or ""),
        **DbField(model, fld).__dict__,
    )
    try:
        obj = data_dictionary_model_cls.objects.get(
            field_name=fld[0], model=model._meta.label_lower
        )
    except ObjectDoesNotExist:
        data_dictionary_model_cls.objects.create(**options)
    else:
        for k, v in options.items():
            setattr(obj, k, v)
        obj.save()


def populate_data_dictionary(form=None, model=None):
    try:
        auto_number = form._meta.auto_number
    except AttributeError:
        auto_number = True
    finally:
        if auto_number:
            for index, fld in enumerate(form.base_fields.items()):
                create_or_update_data_dictionary(index, model, fld)


def populate_data_dictionary_from_sites(request=None):

    try:
        app_labels = settings.DATA_DICTIONARY_APP_LABELS
    except AttributeError:
        warn("Settings attribute DATA_DICTIONARY_APP_LABELS not set.")
        app_labels = []

    if not request:
        rf = RequestFactory()
        request = rf.get("/")
        # DataManagerUser.objects.all()[0]
        request.user = DataManagerUser(
            id=1, username="erikvw", is_superuser=True, is_active=True
        )
    DataDictionary.objects.update(active=False)
    for site in sites.all_sites.data:
        for model_admin in site()._registry.values():
            form = model_admin.get_form(request)
            model = model_admin.model
            if model._meta.app_label in app_labels and not issubclass(
                model, (ListModelMixin,)
            ):
                sys.stdout.write(f"  * {model._meta.label_lower}.\n")
                populate_data_dictionary(form=form, model=model)
