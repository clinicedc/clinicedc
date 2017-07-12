from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class PredicateCollection:

    app_label = 'edc_metadata'
    reference_model = 'edc_reference.reference'

    def __init__(self):
        self.reference_model_cls = django_apps.get_model(self.reference_model)

    def exists(self, **kwargs):
        return self.get_reference_object(**kwargs)

    def exists_for_value(self, value=None, **kwargs):
        reference_object = self.get_reference_object(**kwargs)
        try:
            reference_value = reference_object.value
        except AttributeError:
            reference_value = None
        return reference_value == value

    def get_reference_object(self, model=None, visit=None, subject_identifier=None, **kwargs):
        try:
            model.split('.')[1]
        except IndexError:
            model = f'{self.app_label}.{model}'
        if visit:
            kwargs.update(identifier=subject_identifier,
                          report_datetime=visit.report_datetime)
        elif subject_identifier:
            kwargs.update(identifier=subject_identifier)
        try:
            reference_object = self.reference_model_cls.objects.get(
                model=model, **kwargs)
        except ObjectDoesNotExist:
            reference_object = None
        return reference_object
