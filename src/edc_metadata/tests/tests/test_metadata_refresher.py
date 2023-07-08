from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_visit_schedule import (
    Crf,
    FormsCollection,
    Schedule,
    Visit,
    VisitSchedule,
    site_visit_schedules,
)
from edc_visit_tracking.constants import SCHEDULED

from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.metadata_refresher import MetadataRefresher
from edc_metadata.models import CrfMetadata

from ..models import CrfFive, CrfOne, SubjectVisit
from .metadata_test_mixin import TestMetadataMixin


class TestMetadataRefresher(TestMetadataMixin, TestCase):
    def check(self, expected, subject_visit=None):
        for model, entry_status in expected.items():
            with self.subTest(model=model, entry_status=entry_status):
                try:
                    CrfMetadata.objects.filter(
                        entry_status=KEYED,
                        model="edc_metadata.crfone",
                        visit_code=subject_visit.visit_code,
                    )
                except ObjectDoesNotExist:
                    self.fail(
                        f"CrfMetadata unexpectedly does not exist. Got {model}, {entry_status}"
                    )

    def test_updates_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfMetadata.objects.all().delete()
        expected = {
            "edc_metadata.crfone": KEYED,
            "edc_metadata.crftwo": REQUIRED,
            "edc_metadata.crfthree": REQUIRED,
        }
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        self.check(expected, subject_visit=subject_visit)

    def test_updates_after_manual_change(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfMetadata.objects.all().delete()
        expected = {
            "edc_metadata.crfone": KEYED,
            "edc_metadata.crftwo": REQUIRED,
            "edc_metadata.crfthree": REQUIRED,
        }
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        crf_metadata = CrfMetadata.objects.get(model="edc_metadata.crfone")
        crf_metadata.entry_status = REQUIRED
        crf_metadata.save()
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        self.check(expected, subject_visit=subject_visit)

    def test_updates_after_manual_change2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        CrfMetadata.objects.all().delete()
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        expected = {
            "edc_metadata.crfone": REQUIRED,
            "edc_metadata.crftwo": REQUIRED,
            "edc_metadata.crfthree": REQUIRED,
        }
        crf_metadata = CrfMetadata.objects.get(model="edc_metadata.crfone")
        crf_one.delete()
        crf_metadata.entry_status = KEYED
        crf_metadata.save()
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        self.check(expected, subject_visit=subject_visit)

    @staticmethod
    def register_new_visit_schedule(crfs):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False

        visit = Visit(
            code="1000",
            title="Week 1",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            crfs=crfs,
            allow_unscheduled=True,
            facility_name="5-day-clinic",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_metadata.onschedule",
            offschedule_model="edc_metadata.offschedule",
            consent_model="edc_metadata.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        schedule.add_visit(visit)
        new_visit_schedule = VisitSchedule(
            name="visit_schedule",
            offstudy_model="edc_offstudy.subjectoffstudy",
            death_report_model="edc_metadata.deathreport",
        )
        new_visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(new_visit_schedule)

    def test_after_schedule_change(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfFive.objects.create(subject_visit=subject_visit)
        self.assertEqual(CrfMetadata.objects.all().count(), 5)
        crfs = FormsCollection(
            Crf(show_order=1, model="edc_metadata.crfone", required=True),
            Crf(show_order=2, model="edc_metadata.crftwo", required=True),
            Crf(show_order=3, model="edc_metadata.crfthree", required=True),
            Crf(show_order=4, model="edc_metadata.crffour", required=True),
        )
        self.register_new_visit_schedule(crfs)
        self.assertEqual(CrfMetadata.objects.all().count(), 5)
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        # CrfFive is no longer in visit schedule, so one less
        # CRFMetadata instance
        self.assertEqual(CrfMetadata.objects.all().count(), 4)
        expected = {
            "edc_metadata.crfone": REQUIRED,
            "edc_metadata.crftwo": REQUIRED,
            "edc_metadata.crfthree": REQUIRED,
            "edc_metadata.crfFour": REQUIRED,
        }
        self.check(expected, subject_visit=subject_visit)

    def test_after_schedule_change2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertEqual(CrfMetadata.objects.all().count(), 5)
        crfs = FormsCollection(
            Crf(show_order=1, model="edc_metadata.crfone", required=True),
            Crf(show_order=2, model="edc_metadata.crftwo", required=True),
            Crf(show_order=3, model="edc_metadata.crfthree", required=True),
            Crf(show_order=4, model="edc_metadata.crffour", required=True),
        )
        self.register_new_visit_schedule(crfs)
        self.assertEqual(CrfMetadata.objects.all().count(), 5)
        metadata_refresher = MetadataRefresher()
        metadata_refresher.run()
        self.assertEqual(CrfMetadata.objects.all().count(), 4)
        expected = {
            "edc_metadata.crfone": REQUIRED,
            "edc_metadata.crftwo": REQUIRED,
            "edc_metadata.crfthree": REQUIRED,
            "edc_metadata.crfFour": REQUIRED,
        }
        self.check(expected, subject_visit=subject_visit)
