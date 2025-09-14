from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

from edc_consent.form_validators import ConsentDefinitionFormValidatorMixin
from edc_form_validators import ReportDatetimeFormValidatorMixin
from edc_utils import age, to_utc
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_tracking.modelform_mixins import get_related_visit

if TYPE_CHECKING:
    from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    class RelatedVisitModel(SiteModelMixin, CreatesMetadataModelMixin, Base, BaseUuidModel):
        pass


__all__ = ["BaseFormValidatorMixin", "CrfFormValidatorMixin"]


class BaseFormValidatorMixin(
    ReportDatetimeFormValidatorMixin, ConsentDefinitionFormValidatorMixin
):
    """A base mixin of common properties needed for PRN/CRF validation
    to be declared with FormValidators.
    """

    @property
    def subject_identifier(self) -> str | None:
        if "subject_identifier" in self.cleaned_data:
            subject_identifier = self.cleaned_data.get("subject_identifier")
        else:
            subject_identifier = getattr(self.instance, "subject_identifier", None)
        return subject_identifier

    @property
    def age_in_years(self) -> int | None:
        if self.report_datetime and self.subject_consent.dob:
            return age(self.subject_consent.dob, to_utc(self.report_datetime)).years
        return None


class CrfFormValidatorMixin(BaseFormValidatorMixin):
    """Assumes model is a CRF and has a key to related/subject_visit.

    Declare with FormValidator (not modelform).
    """

    @property
    def subject_identifier(self) -> str:
        """Always returns the subject_identifier from related_visit"""
        return self.related_visit.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        """Returns report_datetime or raises.

        Report datetime is always a required field on a CRF model,
        Django will raise a field ValidationError before getting
        here if report_datetime is None.
        """
        report_datetime = None
        if self.report_datetime_field_attr in self.cleaned_data:
            report_datetime = self.cleaned_data.get(self.report_datetime_field_attr)
        elif self.instance:
            report_datetime = self.instance.report_datetime
        return report_datetime

    @property
    def related_visit_model_attr(self) -> str:
        return self.model.related_visit_model_attr()

    @property
    def related_visit(self) -> RelatedVisitModel:
        """Returns a subject visit model instance or None"""
        return get_related_visit(self, related_visit_model_attr=self.related_visit_model_attr)

    @property
    def related_visit_model_cls(self) -> type[RelatedVisitModel]:
        """Returns a subject visit model instance or None"""
        return get_related_visit(
            self, related_visit_model_attr=self.related_visit_model_attr
        ).__class__

    @property
    def visit_schedule(self) -> VisitSchedule:
        return self.related_visit.visit_schedule

    @property
    def schedule(self) -> Schedule:
        return self.related_visit.schedule

    @property
    def offschedule_datetime(self) -> datetime | None:
        try:
            obj = self.related_visit.schedule.offschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            offschedule_datetime = None
        else:
            offschedule_datetime = obj.offschedule_datetime
        return offschedule_datetime
