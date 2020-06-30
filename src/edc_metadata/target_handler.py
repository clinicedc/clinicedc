from django.apps import apps as django_apps
from edc_reference import site_reference_configs

from edc_metadata.constants import CRF
from edc_metadata.metadata_handler import MetadataHandler
from edc_visit_tracking.constants import MISSED_VISIT


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

    If visit reason is MISSED_VISIT, returns None.

    If target model is not scheduled for this visit a
    TargetModelNotScheduledForVisit exception will be raised.
    """

    metadata_handler_cls = MetadataHandler
    metadata_category = CRF
    metadata_model = "edc_metadata.crfmetadata"

    def __init__(self, model=None, visit_model_instance=None):

        self.model = model
        self.visit_model_instance = visit_model_instance  # visit model instance
        self.metadata_model_cls = django_apps.get_model(
            self.metadata_model
        )  # .get_metadata_model(self.metadata_category)

        if self.model == self.visit_model_instance._meta.label_lower:
            raise TargetModelConflict(
                f"Target model and visit model are the same! "
                f"Got {self.model}=={self.visit_model_instance._meta.label_lower}"
            )

        try:
            django_apps.get_model(self.model)
        except LookupError as e:
            raise TargetModelLookupError(
                f"{self.metadata_category} target model name is invalid. Got {e}"
            )

        if self.visit_model_instance.reason == MISSED_VISIT:
            self.metadata_obj = None
        else:
            self.raise_on_not_scheduled_for_visit()
            self.metadata_obj = self.metadata_handler.metadata_obj

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.model}, {self.visit_model_instance}), "
            f"{self.metadata_model_cls._meta.label_lower}>"
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
            name=self.model, visit=self.visit_model_instance
        )

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.model,
            visit_model_instance=self.visit_model_instance,
        )

    @property
    def models(self):
        """Returns a list of models for this visit.
        """
        if self.visit_model_instance.visit_code_sequence != 0:
            forms = (
                self.visit_model_instance.visit.unscheduled_forms
                + self.visit_model_instance.visit.prn_forms
            )
        elif self.visit_model_instance.reason == MISSED_VISIT:
            forms = self.visit_model_instance.visit.missed_forms
        else:
            forms = (
                self.visit_model_instance.visit.forms
                + self.visit_model_instance.visit.prn_forms
            )
        return list(set([form.model for form in forms]))

    def raise_on_not_scheduled_for_visit(self):
        """Raises an exception if model is not scheduled
        for this visit.

        PRN forms are added to the list of scheduled forms
        for the conditional eval.
        """
        if self.model not in self.models:
            raise TargetModelNotScheduledForVisit(
                f"Target model `{self.model}` is not scheduled "
                f"(nor a PRN) for visit '{self.visit_model_instance.visit_code}'."
            )
