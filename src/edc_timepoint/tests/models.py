from edc_consent.field_mixins import IdentityFieldsMixin, PersonalFieldsMixin
from edc_consent.model_mixins import ConsentModelMixin
from edc_crf.model_mixins import CrfModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_reference.model_mixins import ReferenceModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin

from ..model_mixins import TimepointLookupModelMixin
from ..timepoint_lookup import TimepointLookup


class VisitTimepointLookup(TimepointLookup):
    timepoint_model = "edc_appointment.appointment"
    timepoint_related_model_lookup = "appointment"


class CrfTimepointLookup(TimepointLookup):
    timepoint_model = "edc_appointment.appointment"


class SubjectConsent(
    SiteModelMixin,
    ConsentModelMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    UniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    def natural_key(self):
        return (self.subject_identifier,)

    class Meta(ConsentModelMixin.Meta, BaseUuidModel.Meta):
        pass


class SubjectVisit(
    SiteModelMixin,
    VisitModelMixin,
    ReferenceModelMixin,
    CreatesMetadataModelMixin,
    TimepointLookupModelMixin,
    BaseUuidModel,
):
    timepoint_lookup_cls = VisitTimepointLookup

    class Meta(VisitModelMixin.Meta):
        pass


class CrfOne(CrfModelMixin, TimepointLookupModelMixin, BaseUuidModel):
    timepoint_lookup_cls = CrfTimepointLookup


class CrfTwo(CrfModelMixin, TimepointLookupModelMixin, BaseUuidModel):
    timepoint_lookup_cls = CrfTimepointLookup


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    pass


class DeathReport(SiteModelMixin, UniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)
