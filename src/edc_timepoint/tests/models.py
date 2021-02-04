from edc_consent.field_mixins import IdentityFieldsMixin, PersonalFieldsMixin
from edc_consent.model_mixins import ConsentModelMixin
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin, VisitTrackingCrfModelMixin

from ..model_mixins import TimepointLookupModelMixin
from ..timepoint_lookup import TimepointLookup


class VisitTimepointLookup(TimepointLookup):
    timepoint_model = "edc_appointment.appointment"
    timepoint_related_model_lookup = "appointment"


class CrfTimepointLookup(TimepointLookup):
    timepoint_model = "edc_appointment.appointment"


class SubjectConsent(
    ConsentModelMixin,
    PersonalFieldsMixin,
    IdentityFieldsMixin,
    UniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)


# class SubjectVisit(
#     VisitModelMixin,
#     ReferenceModelMixin,
#     CreatesMetadataModelMixin,
#     SiteModelMixin,
#     BaseUuidModel,
# ):
#
#     subject_identifier = models.CharField(max_length=50)


class SubjectVisit(VisitModelMixin, TimepointLookupModelMixin, BaseUuidModel):

    timepoint_lookup_cls = VisitTimepointLookup

    class Meta(VisitModelMixin.Meta):
        pass


class CrfOne(VisitTrackingCrfModelMixin, TimepointLookupModelMixin, BaseUuidModel):

    timepoint_lookup_cls = CrfTimepointLookup


class CrfTwo(VisitTrackingCrfModelMixin, TimepointLookupModelMixin, BaseUuidModel):

    timepoint_lookup_cls = CrfTimepointLookup


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    pass


class DeathReport(UniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)
