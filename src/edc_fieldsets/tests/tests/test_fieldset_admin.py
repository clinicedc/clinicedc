from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.contrib.sites.models import Site
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
from edc_utils import get_utcnow
from edc_visit_schedule.models import OnSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from ..admin import VISIT_ONE, VISIT_TWO
from ..models import MyModel, MyModel2, SubjectConsentV1
from ..visit_schedule import get_visit_schedule


@override_settings(
    SITE_ID=10,
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2018, 6, 10, 0, 00, tzinfo=ZoneInfo("UTC")),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2027, 6, 10, 0, 00, tzinfo=ZoneInfo("UTC")),
)
class TestFieldsetAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(id=10, name="site_ten", domain="clinicedc.org")

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
        site_sites.register(site10)

        consent_v1 = ConsentDefinition(
            "edc_fieldsets.subjectconsentv1",
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
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

    def setUp(self):
        test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(test_datetime)
        traveller.start()

        self.user = User.objects.create(username="erikvw", is_staff=True, is_active=True)
        for permission in Permission.objects.filter(content_type__app_label="edc_fieldsets"):
            self.user.user_permissions.add(permission)

        self.subject_identifier = "1234"
        SubjectConsentV1.objects.create(
            subject_identifier="1234",
            consent_datetime=get_utcnow(),
            site_id=10,
        )

        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
            skip_get_current_site=True,
        )
        traveller.stop()

    def test_fieldset_excluded(self):
        """Asserts the conditional fieldset is not added
        to the model admin instance for this appointment.

        VISIT_ONE
        """
        appointment = Appointment.objects.get(visit_code=VISIT_ONE)
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)
        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")

        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
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
        appointment = Appointment.objects.get(visit_code=VISIT_ONE)
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(visit_code=VISIT_TWO)
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")
        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertIn("form-row field-f1", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f2", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f3", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f4", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f5", rendered_change_form.rendered_content)

    @tag("1")
    @override_settings(SITE_ID=10)
    def test_fieldset_moved_to_end(self):
        """Asserts the conditional fieldset IS inserted
        but `Summary` and `Audit` fieldsets remain at the end.

        VISIT_TWO
        """
        test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(test_datetime)
        traveller.start()
        appointment = Appointment.objects.get(visit_code=VISIT_ONE)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()

        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()

        traveller.stop()
        test_datetime = datetime(2019, 6, 12, 8, 00, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(test_datetime)
        traveller.start()

        appointment = Appointment.objects.get(visit_code=VISIT_TWO)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()

        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)

        for model, model_admin in admin.site._registry.items():
            if model == MyModel2:
                my_model_admin = model_admin.admin_site._registry.get(MyModel2)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")
        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertLess(
            rendered_change_form.rendered_content.find("id_f4"),
            rendered_change_form.rendered_content.find("id_summary_one"),
        )
