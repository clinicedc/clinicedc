import sys
from inspect import isfunction
from warnings import warn

from django.apps import apps as django_apps
from django.contrib.admin import sites
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db.models.fields import NOT_PROVIDED
from django.db.utils import IntegrityError, OperationalError
from django.test.client import RequestFactory
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from edc_list_data.model_mixins import ListModelMixin

from .models import DataDictionary, DataManagerUser

WIDGET = 1
FIELD_NAME = 0


class DbField:
    def __init__(self, model, fld):
        try:
            db_field = model._meta.get_field(get_field_name(fld))
        except FieldDoesNotExist:
            pass
        else:
            self.decimal_places = getattr(db_field, "decimal_places", None)
            self.default = self.get_default(db_field)
            self.field_name = getattr(db_field, "name", None)
            self.field_type = None if db_field is None else db_field.get_internal_type()
            self.help_text = format_html(
                "{}", mark_safe(getattr(db_field, "help_text", ""))  # nosec B703, B308
            )
            self.max_digits = getattr(db_field, "max_digits", None)
            self.max_length = getattr(db_field, "max_length", None)
            self.nullable = getattr(db_field, "null", False)

    @staticmethod
    def get_default(db_field):
        default = getattr(db_field, "default", None)
        if default == NOT_PROVIDED:
            default = None
        if isfunction(default):
            default = default.__name__
        return default


def get_field_name(fld):
    try:
        return fld[FIELD_NAME]
    except TypeError:
        return fld.name


def get_form_field_type(model, fld):
    field_type = None
    try:
        db_field = model._meta.get_field(fld[FIELD_NAME])
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
    try:
        label = get_form_label(fld)
    except TypeError:
        label = fld.verbose_name
    db_field_data = DbField(model, fld).__dict__
    if db_field_data.get("field_name"):
        options = dict(
            active=True,
            model=model._meta.label_lower,
            number=index + 1,
            prompt=format_html("{}", mark_safe(label or "")),  # nosec B703, B308
            **db_field_data,
        )
        try:
            obj = data_dictionary_model_cls.objects.get(
                field_name=get_field_name(fld), model=model._meta.label_lower
            )
        except ObjectDoesNotExist:
            try:
                data_dictionary_model_cls.objects.create(**options)
            except (OperationalError, IntegrityError) as e:
                warn(
                    f"Error when creating DataDictionary instance. " f"Model={model}. Got {e}"
                )
        else:
            for k, v in options.items():
                setattr(obj, k, v)
            obj.save()


def populate_data_dictionary(form=None, model=None):
    auto_number = True
    try:
        auto_number = form._meta.auto_number
    except AttributeError:
        auto_number = True
    finally:
        if auto_number:
            for index, fld in enumerate(form.base_fields.items()):
                create_or_update_data_dictionary(index, model, fld)


def populate_data_dictionary_from_sites(request=None):
    """Populates the DataDictionary model using ModelAdmin
    classes.

    Set ModelAdmin.exclude_from_data_dictionary = True to exclude a model.

    If a form class has no base_fields falls back on editable model class fields.
    """

    app_labels = [app_config.name for app_config in django_apps.get_app_configs()]
    if not request:
        rf = RequestFactory()
        request = rf.get("/")
        request.user = DataManagerUser(
            id=1, username="erikvw", is_superuser=True, is_active=True
        )
    DataDictionary.objects.update(active=False)
    for site in sites.all_sites.data:
        sys.stdout.write(f" * {site().name} ...\n")
        for model_admin in site()._registry.values():
            form = model_admin.get_form(request)
            model = model_admin.model
            if model._meta.app_label in app_labels and not issubclass(
                model, (ListModelMixin,)
            ):
                populate = getattr(model_admin, "populate_data_dictionary", True)
                if not populate:
                    sys.stdout.write(f"   - {model._meta.label_lower}. (skipping)\n")
                else:
                    sys.stdout.write(f"   + {model._meta.label_lower}...\n")
                    if not form.base_fields:
                        for index, fld in enumerate(model._meta.get_fields()):
                            if fld.editable:
                                create_or_update_data_dictionary(index, model, fld)
                    else:
                        for index, fld in enumerate(form.base_fields.items()):
                            create_or_update_data_dictionary(index, model, fld)
                    sys.stdout.write(f"   + {model._meta.label_lower}.   \n")
