from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_metadata import NOT_REQUIRED, REQUIRED
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..metadata_updater import MetadataUpdater
from ..models import CrfMetadata, RequisitionMetadata
from ..target_handler import TargetModelLookupError, TargetModelNotScheduledForVisit
from .models import SubjectVisit, SubjectConsent
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestMetadataUpdater(TestCase):
    def setUp(self):
        import_holidays()
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        for visit in self.schedule.visits.values():
            appointment = Appointment.objects.get(
                subject_identifier=self.subject_identifier, visit_code=visit.code
            )
            SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=self.subject_identifier,
                reason=SCHEDULED,
            )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        self.subject_visit = SubjectVisit.objects.get(appointment=self.appointment)

    def test_crf_updates_ok(self):
        CrfMetadata.objects.get(
            visit_code=self.subject_visit.visit_code,
            model="edc_metadata.crfone",
            entry_status=REQUIRED,
        )
        metadata_updater = MetadataUpdater(
            visit=self.subject_visit, target_model="edc_metadata.crfone"
        )
        metadata_updater.update(entry_status=NOT_REQUIRED)
        self.assertRaises(
            ObjectDoesNotExist,
            CrfMetadata.objects.get,
            visit_code=self.subject_visit.visit_code,
            model="edc_metadata.crfone",
            entry_status=REQUIRED,
        )

        for visit_obj in SubjectVisit.objects.all():
            if visit_obj == self.subject_visit:
                try:
                    CrfMetadata.objects.get(
                        visit_code=visit_obj.visit_code,
                        model="edc_metadata.crfone",
                        entry_status=NOT_REQUIRED,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(e)
            else:
                self.assertRaises(
                    ObjectDoesNotExist,
                    CrfMetadata.objects.get,
                    visit_code=visit_obj.visit_code,
                    model="edc_metadata.crfone",
                    entry_status=NOT_REQUIRED,
                )

    def test_crf_invalid_model(self):
        metadata_updater = MetadataUpdater(
            visit=self.subject_visit, target_model="edc_metadata.blah"
        )
        self.assertRaises(
            TargetModelLookupError, metadata_updater.update, entry_status=NOT_REQUIRED
        )

    def test_crf_model_not_scheduled(self):
        metadata_updater = MetadataUpdater(
            visit=self.subject_visit, target_model="edc_metadata.crfseven"
        )
        self.assertRaises(
            TargetModelNotScheduledForVisit,
            metadata_updater.update,
            entry_status=NOT_REQUIRED,
        )
