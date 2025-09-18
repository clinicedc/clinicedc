from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.labs import lab_profile
from clinicedc_tests.models import EgfrDropNotification, ResultCrf, SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_constants.constants import BLACK, CLOSED, COMPLETE, INCOMPLETE, MALE, OPEN
from edc_egfr.egfr import Egfr
from edc_facility.import_holidays import import_holidays
from edc_lab import site_labs
from edc_lab.models import Panel
from edc_lab_panel.panels import rft_panel
from edc_reportable import MICROMOLES_PER_LITER
from edc_reportable.data.grading_data.daids_july_2017 import grading_data
from edc_reportable.data.normal_data.africa import normal_data
from edc_reportable.utils import load_reference_ranges
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("egfr")
@override_settings(EDC_SITES_REGISTER_DEFAULT=True, EDC_SITES_CREATE_DEFAULT=True, SITE_ID=10)
class TestEgfr(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_reference_ranges(
            "my_reference_list", normal_data=normal_data, grading_data=grading_data
        )
        site_labs.initialize()
        site_labs.register(lab_profile=lab_profile)
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self) -> None:
        helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            ethnicity=BLACK,
            gender=MALE,
        )

        panel = Panel.objects.get(name=rft_panel.name)

        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
            panel=panel,
        )
        self.crf = ResultCrf.objects.create(
            subject_visit=self.subject_visit,
            requisition=requisition,
            report_datetime=self.subject_visit.report_datetime,
            assay_datetime=self.subject_visit.report_datetime,
            egfr_value=156.43,
            creatinine_value=53,
            creatinine_units=MICROMOLES_PER_LITER,
        )
        self.opts = dict(
            gender=MALE,
            age_in_years=30,
            ethnicity=BLACK,
            report_datetime=timezone.now(),
            reference_range_collection_name="my_reference_list",
            formula_name="ckd-epi",
        )

    @override_settings(EDC_EGFR_DROP_NOTIFICATION_MODEL="clinicedc_tests.EgfrDropNotification")
    def test_egfr_drop_notification_model(self):
        Egfr(
            baseline_egfr_value=220.1,
            percent_drop_threshold=20,
            calling_crf=self.crf,
            **self.opts,
        )
        obj = EgfrDropNotification.objects.get(subject_visit=self.subject_visit)
        obj.report_status = OPEN
        obj.save()
        self.assertEqual(obj.crf_status, INCOMPLETE)
        obj.report_status = CLOSED
        obj.save()
        self.assertEqual(obj.crf_status, COMPLETE)
