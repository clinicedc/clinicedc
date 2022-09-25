from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from edc_reference import site_reference_configs
from edc_visit_tracking.constants import MISSED_VISIT

from edc_metadata.constants import CRF
from edc_metadata.metadata_handler import MetadataHandler

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin


class TargetModelNotScheduledForVisit(Exception):
    pass


class TargetModelConflict(Exception):
    pass


class TargetModelMissingManagerMethod(Exception):
    pass


class TargetModelLookupError(Exception):
    pass


class TargetModelMissingMetadata(Exception):
    pass


class TargetHandler:

    """A class that gets the target model "model instance"
    for a given visit, if it exists.

    If target model is not scheduled for this visit a
    TargetModelNotScheduledForVisit exception will be raised.
    """

    metadata_handler_cls = MetadataHandler
    metadata_category = CRF
    metadata_model = "edc_metadata.crfmetadata"

    def __init__(self, model: str = None, related_visit: VisitModelMixin = None):

        self.model = model
        self.related_visit = related_visit  # visit model instance
        self.metadata_model_cls = django_apps.get_model(
            self.metadata_model
        )  # .get_metadata_model(self.metadata_category)
        if self.model == self.related_visit._meta.label_lower:
            raise TargetModelConflict(
                f"Target model and visit model are the same! "
                f"Got {self.model}=={self.related_visit._meta.label_lower}"
            )

        try:
            django_apps.get_model(self.model)
        except LookupError as e:
            raise TargetModelLookupError(
                f"{self.metadata_category} target model name is invalid. Got {e}"
            )
        if self.related_visit.reason != MISSED_VISIT:
            self.raise_on_not_scheduled_for_visit()
        self.metadata_obj = self.metadata_handler.metadata_obj
        if not self.metadata_obj and related_visit.reason != MISSED_VISIT:
            raise TargetModelMissingMetadata(
                f"{self.metadata_model} model instance unexpectedly does not exist! "
                f"Got model: `{model}` visit: `{related_visit}`. "
                f"visit reason={related_visit.reason}`."
            )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.model}, {self.related_visit}), "
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
            name=self.model, visit=self.related_visit
        )

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.model,
            related_visit=self.related_visit,
        )

    @property
    def models(self):
        """Returns a list of models for this visit."""
        if self.related_visit.visit_code_sequence != 0:
            forms = (
                self.related_visit.visit.unscheduled_forms + self.related_visit.visit.prn_forms
            )
        elif self.related_visit.reason == MISSED_VISIT:
            forms = self.related_visit.visit.missed_forms
        else:
            forms = self.related_visit.visit.forms + self.related_visit.visit.prn_forms
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
                f"(nor a PRN) for visit '{self.related_visit.visit_code}."
                f"{self.related_visit.visit_code_sequence}' "
                f"subject '{self.related_visit.subject_identifier}'."
            )
