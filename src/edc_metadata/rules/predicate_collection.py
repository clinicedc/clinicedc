from django.apps import apps as django_apps

from edc_reference import LongitudinalRefset, site_reference_configs


class PredicateCollection:

    app_label = 'edc_metadata'
    visit_model = None

    def __init__(self):
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(self.visit_model))

    def values(self, value=None, field_name=None, **kwargs):
        """Returns a list of matching values or an empty list.
        """
        return self.exists(value=value, field_name=field_name, **kwargs)

    def exists(self, value=None, field_name=None, **kwargs):
        """Returns a list of values, all or filtered, or an empty
        list.
        """
        refsets = self.refsets(**kwargs)
        if value:
            return refsets.fieldset(field_name).filter(value).values
        else:
            return refsets.fieldset(field_name).all().values

    def refsets(self, model=None, **options):
        try:
            model.split('.')[1]
        except IndexError:
            model = f'{self.app_label}.{model}'
        refsets = LongitudinalRefset(
            visit_model=self.visit_model,
            model=model,
            reference_model_cls=self.reference_model_cls,
            **options)
        return refsets
