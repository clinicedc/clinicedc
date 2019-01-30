from django.apps import apps as django_apps
from edc_reference import site_reference_configs

from .constants import CRF
from .metadata_handler import MetadataHandler


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

    metadata_handler_cls = MetadataHandler
    metadata_category = CRF

    def __init__(self, model=None, visit=None, **kwargs):

        self.model = model
        self.visit = visit  # visit model instance
        self.metadata_model = django_apps.get_app_config(
            "edc_metadata"
        ).get_metadata_model(self.metadata_category)

        if self.model == self.visit._meta.label_lower:
            raise TargetModelConflict(
                f"Target model and visit model are the same! "
                f"Got {self.model}=={self.visit._meta.label_lower}"
            )

        try:
            django_apps.get_model(self.model)
        except LookupError as e:
            raise TargetModelLookupError(
                f"{self.metadata_category} target model name is invalid. Got {e}"
            )

        self.raise_on_not_scheduled_for_visit()

        self.metadata_obj = self.metadata_handler.metadata_obj

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.model}, {self.visit}), "
            f"{self.metadata_model._meta.label_lower}>"
        )

    @property
    def reference_model_cls(self):
        reference_model = site_reference_configs.get_reference_model(name=self.model)
        return django_apps.get_model(reference_model)

    @property
    def object(self):
        """Returns a reference model instance for the "target".

        Recall the CRF/Requisition is not queried directly but rather
        represented by a model instance from edc_reference.
        """
        return self.reference_model_cls.objects.filter_crf_for_visit(
            name=self.model, visit=self.visit
        )

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model, model=self.model, visit=self.visit
        )

    @property
    def models(self):
        """Returns a list of models for this visit.
        """
        if self.visit.visit_code_sequence != 0:
            forms = self.visit.visit.unscheduled_forms + self.visit.visit.prn_forms
        else:
            forms = self.visit.visit.forms + self.visit.visit.prn_forms
        return list(set([form.model for form in forms]))

    def raise_on_not_scheduled_for_visit(self):
        """Raises an exception if model is not scheduled
        for this visit.

        PRN forms are added to the list of scheduled forms
        for the conditional eval.
        """
        if self.model not in self.models:
            raise TargetModelNotScheduledForVisit(
                f"Target model {self.model} is not scheduled "
                f"for visit '{self.visit.visit_code}'."
            )
