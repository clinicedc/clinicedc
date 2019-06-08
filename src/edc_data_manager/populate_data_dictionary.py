import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from warnings import warn
from django.test.client import RequestFactory
from django.conf import settings
from django.contrib.admin import sites
from edc_data_manager.models import DataDictionary
from edc_list_data.model_mixins import ListModelMixin
from edc_data_manager.models import DataManagerUser


WIDGET = 1


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
    data_dictionary_model_cls = django_apps.get_model(
        "edc_data_manager.datadictionary")
    field_type = get_form_field_type(model, fld)
    label = get_form_label(fld)
    options = dict(
        active=True,
        field_name=fld[0],
        field_type=field_type,
        model=model._meta.label_lower,
        number=index + 1,
        prompt=label,
    )
    try:
        obj = data_dictionary_model_cls.objects.get(
            field_name=fld[0], model=model._meta.label_lower
        )
    except ObjectDoesNotExist:
        data_dictionary_model_cls.objects.create(**options)
    else:
        obj.active = True
        obj.field_type = field_type
        obj.number = index + 1
        obj.prompt = label
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
    if not request:
        rf = RequestFactory()
        request = rf.get("/")
        request.user = DataManagerUser.objects.all()[0]
    DataDictionary.objects.update(active=False)
    for site in sites.all_sites.data:
        for model_admin in site()._registry.values():
            form = model_admin.get_form(request)
            model = model_admin.model
            if model._meta.app_label in settings.DATA_DICTIONARY_APP_LABELS and not issubclass(
                model, (ListModelMixin,)
            ):
                sys.stdout.write(f"  * {model._meta.label_lower}.\n")
                populate_data_dictionary(form=form, model=model)
