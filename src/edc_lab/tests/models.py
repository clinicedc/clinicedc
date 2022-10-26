from django.db import models
from edc_consent.field_mixins.identity_fields_mixin import IdentityFieldsMixin
from edc_consent.field_mixins.personal_fields_mixin import PersonalFieldsMixin
from edc_consent.model_mixins.consent_model_mixin import ConsentModelMixin
from edc_crf.model_mixins import CrfModelMixin, CrfWithActionModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_reference import ReferenceModelConfig, site_reference_configs
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_screening.model_mixins import ScreeningModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import (
    OffScheduleModelMixin,
    OnScheduleModelMixin,
    SubjectOnScheduleModelMixin,
    VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
)
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)

from edc_lab.model_mixins import RequisitionModelMixin

site_reference_configs.registry = {}
reference = ReferenceModelConfig(name="edc_lab.subjectrequisition.panel", fields=["panel"])
site_reference_configs.register(reference)
reference = ReferenceModelConfig(name="edc_lab.CrfOne", fields=["f1"])
site_reference_configs.register(reference)


class SubjectRequisitionManager(models.Manager):
    def get_by_natural_key(self, requisition_identifier, subject_identifier, report_datetime):
        subject_visit = SubjectVisit.objects.get(
            subject_identifier=subject_identifier, report_datetime=report_datetime
        )
        return self.get(
            requisition_identifier=requisition_identifier, subject_visit=subject_visit
        )


class SubjectVisit(SiteModelMixin, VisitModelMixin, CreatesMetadataModelMixin, BaseUuidModel):
    def update_reference_on_save(self):
        pass


class SubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Missed Visit Reasons"
        verbose_name_plural = "Subject Missed Visit Reasons"


class SubjectVisitMissed(
    SubjectVisitMissedModelMixin,
    CrfWithActionModelMixin,
    BaseUuidModel,
):

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="+"
    )

    class Meta(
        SubjectVisitMissedModelMixin.Meta,
        BaseUuidModel.Meta,
    ):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"


class SubjectRequisition(RequisitionModelMixin, BaseUuidModel):
    def update_reference_on_save(self):
        pass

    class Meta(RequisitionModelMixin.Meta):
        pass


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):

    pass


class DeathReport(SiteModelMixin, UniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


class SubjectScreening(ScreeningModelMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()


class SubjectConsent(
    SiteModelMixin,
    ConsentModelMixin,
    UniqueSubjectIdentifierFieldMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SubjectOnScheduleModelMixin,
    VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
    BaseUuidModel,
):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)

    class Meta(ConsentModelMixin.Meta):
        pass


class CrfOne(CrfModelMixin, BaseUuidModel):

    dte = models.DateTimeField(default=get_utcnow)
