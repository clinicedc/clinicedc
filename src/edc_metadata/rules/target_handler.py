from django.apps import apps as django_apps


from ..constants import CRF


class TargetModelConflict(Exception):
    pass


class TargetModelMissingManagerMethod(Exception):
    pass


class TargetModelLookupError(Exception):
    pass


class TargetHandler:

    """A class that gets the target model "model instance"
    for a given visit, if it exists.

    The target model "model class" requires manager method `get_for_visit`.
    """

    def __init__(self, model=None, visit=None, metadata_category=None):
        self.model = model
        self.visit = visit
        app_config = django_apps.get_app_config('edc_metadata')
        reference_model = app_config.metadata_reference_model
        self.reference_model_cls = django_apps.get_model(reference_model)
        if model == visit._meta.label_lower:
            raise TargetModelConflict(
                f'Target model and visit model are the same! '
                f'Got {model}=={visit._meta.label_lower}')
        app_config = django_apps.get_app_config('edc_metadata')
        self.metadata_model = app_config.get_metadata_model(
            metadata_category)

    def __repr__(self):
        return (f'<{self.__class__.__name__}({self.model}, {self.visit}), '
                f'{self.metadata_model._meta.label_lower}>')

    @property
    def object(self):
        return self.reference_model_cls.objects.filter_crf_for_visit(
            model=self.model, visit=self.visit)
