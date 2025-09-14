from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import TestModel4, TestModel6
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_sites.single_site import SingleSite
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY01
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Crf, CrfCollection
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

utc_tz = ZoneInfo("UTC")


@tag("fieldsets")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestFieldsetAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        fqdn = "clinicedc.org"
        language_codes = ["en"]
        site10 = SingleSite(
            10,
            "mochudi",
            title="Mochudi",
            country="botswana",
            country_code="bw",
            language_codes=language_codes,
            domain=f"mochudi.bw.{fqdn}",
        )
        site_sites._registry = {}
        site_sites.register(site10)
        add_or_update_django_sites(verbose=True)

        site_consents.registry = {}
        consent_v1 = ConsentDefinition(
            "clinicedc_tests.subjectconsentv1",
            version="1",
            start=ResearchProtocolConfig().study_open_datetime,
            end=ResearchProtocolConfig().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
            site_ids=[10],
        )
        site_consents.register(consent_v1)

        crfs = CrfCollection(
            Crf(show_order=1, model="clinicedc_tests.testmodel3", required=True),
            Crf(show_order=2, model="clinicedc_tests.testmodel4", required=True),
            Crf(show_order=3, model="clinicedc_tests.testmodel5", required=True),
        )

        visit_schedule = get_visit_schedule(consent_v1, crfs=crfs)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            age_in_years=25,
        )

    def setUp(self):
        self.user = User.objects.create(username="erikvw", is_staff=True, is_active=True)
        for permission in Permission.objects.filter(content_type__app_label="clinicedc_tests"):
            self.user.user_permissions.add(permission)

    def test_fieldset_excluded(self):
        """Asserts the conditional fieldset is not added
        to the model admin instance for this appointment.

        VISIT_ONE
        """
        appointment = Appointment.objects.get(visit_code=DAY01)
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        for model, model_admin in admin.site._registry.items():
            if model == TestModel6:
                my_test_model_6_admin = model_admin.admin_site._registry.get(TestModel6)
        rf = RequestFactory()

        request = rf.get(f"/?appointment={appointment.id!s}")

        request.user = self.user

        rendered_change_form = my_test_model_6_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertIn("form-row field-f1", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f2", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f3", rendered_change_form.rendered_content)
        self.assertNotIn("form-row field-f4", rendered_change_form.rendered_content)
        self.assertNotIn("form-row field-f5", rendered_change_form.rendered_content)

    def test_fieldset_included(self):
        """Asserts the conditional fieldset IS added
        to the model admin instance for this appointment.

        VISIT_TWO
        """
        appointment = Appointment.objects.get(visit_code=DAY01)
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(visit_code="2000")
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        for model, model_admin in admin.site._registry.items():
            if model == TestModel6:
                my_test_model_6_admin = model_admin.admin_site._registry.get(TestModel6)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={appointment.id!s}")
        request.user = self.user

        rendered_change_form = my_test_model_6_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertIn("form-row field-f1", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f2", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f3", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f4", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f5", rendered_change_form.rendered_content)

    @override_settings(SITE_ID=10)
    def test_fieldset_moved_to_end(self):
        """Asserts the conditional fieldset IS inserted
        but `Summary` and `Audit` fieldsets remain at the end.

        VISIT_TWO
        """
        test_datetime = datetime(2025, 6, 11, 8, 30, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(test_datetime)
        traveller.start()
        appointment = Appointment.objects.get(visit_code=DAY01)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()

        SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()

        traveller.stop()
        test_datetime = datetime(2025, 6, 12, 8, 00, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(test_datetime)
        traveller.start()

        appointment = Appointment.objects.get(visit_code="2000")
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()

        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )

        for model, model_admin in admin.site._registry.items():
            if model == TestModel4:
                my_test_model_4_admin = model_admin.admin_site._registry.get(TestModel4)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={appointment.id!s}")
        request.user = self.user

        rendered_change_form = my_test_model_4_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertLess(
            rendered_change_form.rendered_content.find("id_f4"),
            rendered_change_form.rendered_content.find("id_summary_one"),
        )
