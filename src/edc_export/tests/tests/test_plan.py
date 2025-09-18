import uuid
from tempfile import mkdtemp

from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import Crf, ListModel
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase, override_settings
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_export.model_exporter import PlanExporter
from edc_export.models import Plan
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.models import SubjectVisit


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp())
class TestPlan(TestCase):
    helper_cls = Helper

    def setUp(self):
        import_holidays()
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        for i in range(0, 7):
            helper = self.helper_cls()
            helper.consent_and_put_on_schedule(
                visit_schedule_name=visit_schedule.name,
                schedule_name="schedule1",
                report_datetime=timezone.now(),
            )
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
            SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=appointment.subject_identifier,
                report_datetime=timezone.now(),
            )
        self.subject_visit = SubjectVisit.objects.all()[0]
        self.thing_one = ListModel.objects.create(display_name="thing_one", name="thing_one")
        self.thing_two = ListModel.objects.create(display_name="thing_two", name="thing_two")
        self.crf = Crf.objects.create(
            subject_visit=self.subject_visit,
            char1="char",
            date1=timezone.now(),
            int1=1,
            uuid1=uuid.uuid4(),
        )

    def test_plan(self):
        plan_name = "test_plan"
        Plan.objects.create(name=plan_name, model="export_app.crf")
        PlanExporter(plan_name=plan_name)
