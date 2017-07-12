from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class PredicateCollection:

    app_label = 'edc_metadata'
    reference_model = 'edc_reference.reference'

    def __init__(self):
        self.reference_model_cls = django_apps.get_model(self.reference_model)

    def exists(self, model=None, visit=None, subject_identifier=None, **kwargs):
        try:
            model.split('.')[1]
        except IndexError:
            model = f'{self.app_label}.{model}'
        if visit:
            kwargs.update(identifier=subject_identifier,
                          report_datetime=visit.report_datetime)
        elif subject_identifier:
            kwargs.update(identifier=subject_identifier)
        return self.get_value(model=model, **kwargs)

    def get_value(self, value=None, **kwargs):
        try:
            reference_object = self.reference_model_cls.objects.get(**kwargs)
        except ObjectDoesNotExist:
            value = None
        else:
            value = reference_object.value
        return value
