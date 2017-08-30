from django.apps import apps as django_apps

from edc_reference import site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class TargetModelNotScheduledForVisit(Exception):
    pass


class TargetModelConflict(Exception):
    pass


class TargetModelMissingManagerMethod(Exception):
    pass


class TargetModelLookupError(Exception):
    pass


class TargetHandler:

    """A class that gets the target model "model instance"
    for a given visit, if it exists.

    If target model is not scheduled for this visit a
    TargetModelNotScheduledForVisit exception will be raised.
    """

    def __init__(self, model=None, visit=None, metadata_category=None, **kwargs):

        self.model = model
        self.visit = visit  # visit model instance

        if self.model == self.visit._meta.label_lower:
            raise TargetModelConflict(
                f'Target model and visit model are the same! '
                f'Got {self.model}=={self.visit._meta.label_lower}')

        try:
            django_apps.get_model(self.model)
        except LookupError as e:
            raise TargetModelLookupError(
                f'{metadata_category} target model name is invalid. Got {e}')

        self.raise_on_not_scheduled_for_visit()

        app_config = django_apps.get_app_config('edc_metadata')
        self.metadata_model = app_config.get_metadata_model(
            metadata_category)
        reference_model = site_reference_configs.get_reference_model(
            self.model)
        self.reference_model_cls = django_apps.get_model(reference_model)

    def __repr__(self):
        return (f'<{self.__class__.__name__}({self.model}, {self.visit}), '
                f'{self.metadata_model._meta.label_lower}>')

    @property
    def object(self):
        return self.reference_model_cls.objects.filter_crf_for_visit(
            model=self.model, visit=self.visit)

    def raise_on_not_scheduled_for_visit(self):
        """Raises an exception if model is not scheduled
        for this visit.
        """
        schedule = site_visit_schedules.get_schedule(
            visit_schedule_name=self.visit.visit_schedule_name,
            schedule_name=self.visit.schedule_name)
        forms = schedule.visits.get(self.visit.visit_code).forms
        models = list(set([form.model for form in forms]))
        if self.model not in models:
            raise TargetModelNotScheduledForVisit(
                f'Target model {self.model} is not scheduled '
                f'for visit \'{self.visit.visit_code}\'.')
