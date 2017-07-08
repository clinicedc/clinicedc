from django.apps import apps as django_apps


class PredicateCollection:

    app_config_name = 'edc_metadata'

    def __init_(self, predicate_models=None):
        self.predicate_models = predicate_models
        if not predicate_models:
            self.model_registry = django_apps.get_app_config(
                self.app_config_name).predicate_models

    def get_model(self, model_name=None):
        return django_apps.get_model(
            **self.predicate_models.get(model_name).split(','))
