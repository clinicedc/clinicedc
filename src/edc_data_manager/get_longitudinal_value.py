from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


class DataDictionaryError(Exception):
    pass


def get_longitudinal_value(subject_identifier=None, reference_dt=None, model=None, field=None):
    DataDictionary = django_apps.get_model("edc_data_manager.datadictionary")
    opts = dict(field_name=field)
    if model:
        opts.update(model=model)
    try:
        data_dictionary = DataDictionary.objects.get(**opts)
    except ObjectDoesNotExist:
        raise DataDictionaryError(
            "Unable to determine longitudinal value. "
            f"Field name '{field}' not found in the data dictionary"
        )
    except MultipleObjectsReturned:
        fields = [
            f"{obj.model}.{obj.field_name}" for obj in DataDictionary.objects.filter(**opts)
        ]
        raise DataDictionaryError(
            "Unable to determine longitudinal value. "
            f"Field name '{field}' is ambiguous. Try specifying the model as well. "
            f"Got {fields}"
        )
    qs = data_dictionary.model_cls.objects.filter(
        subject_visit__appointment__subject_identifier=subject_identifier,
        report_datetime__lte=reference_dt,
    ).order_by("-report_datetime")
    if qs:
        return getattr(qs[0], field)
    return None
