import re
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from django_webtest import WebTest
from edc_auth.auth_updater.group_updater import GroupUpdater, PermissionsCodenameError
from edc_consent import site_consents
from edc_facility import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_test_utils.webtest import login
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import (
    get_related_visit_model,
    get_related_visit_model_cls,
)

from edc_appointment.admin import AppointmentAdmin
from edc_appointment.auth_objects import codenames
from edc_appointment.constants import NEW_APPT
from edc_appointment.tests.helper import Helper
from edc_appointment.utils import get_appointment_model_cls
from edc_appointment_app.consents import v1_consent
from edc_appointment_app.visit_schedule import visit_schedule1


def get_url_name():
    return "subject_dashboard_url"


class TestAdmin(WebTest):
    helper_cls = Helper
    extra_environ = {"HTTP_ACCEPT_LANGUAGE": "en"}

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.user.refresh_from_db()
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=Protocol().study_open_datetime,
        )
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": get_related_visit_model()}
        )

    def get_app_form(self, url_name=None, response=None):
        form = None
        if not response:
            response = self.app.get(
                reverse(url_name), extra_environ={"HTTP_ACCEPT_LANGUAGE": "en"}
            ).maybe_follow()
        for index, form in response.forms.items():
            if form.action == "/i18n/setlang/":
                continue
            else:
                break
        return form

    def login(self):
        form = self.get_app_form("admin:index")
        form["username"] = self.user.username
        form["password"] = "pass"  # nosec B105
        return form.submit()

    @patch.object(
        AppointmentAdmin,
        "get_subject_dashboard_url_name",
        side_effect=get_url_name,
    )
    def test_admin_ok(self, mock_get_subject_dashboard_url_name):
        subject_consent = self.helper.consent_and_put_on_schedule()
        appointments = get_appointment_model_cls().objects.all()
        # there are 4 appts
        self.assertEqual(appointments.count(), 4)
        # all appts are new
        self.assertEqual(
            [appt.appt_status for appt in appointments],
            [NEW_APPT, NEW_APPT, NEW_APPT, NEW_APPT],
        )

        # login
        changelist_url_name = "edc_appointment_admin:edc_appointment_appointment_changelist"
        login(self, user=self.user, redirect_url=changelist_url_name)

        # go to changelist
        url = reverse(changelist_url_name)

        response = self.app.get(url, user=self.user)
        self.assertIn("1000", response.text)
        self.assertIn("2000", response.text)
        self.assertIn("3000", response.text)
        self.assertIn("4000", response.text)
        results = re.findall(r"Not started", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 5)  # one extra for listfilter
        results = re.findall(r"On time", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 1)  # one extra for listfilter
        results = re.findall(r"In Progress", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 1)  # one extra for listfilter

        get_related_visit_model_cls().objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        response = self.app.get(url, user=self.user)
        results = re.findall(r"Not started", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 4)  # one extra for listfilter
        results = re.findall(r"On time", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 2)  # one extra for listfilter
        results = re.findall(r"In Progress", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 2)  # one extra for listfilter

        url = f"{url}?q={subject_consent.subject_identifier}"
        response = self.app.get(url, user=self.user)
        results = re.findall(r"Not started", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 4)  # one extra for listfilter
        results = re.findall(r"On time", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 2)  # one extra for listfilter
        results = re.findall(r"In Progress", response.text, re.IGNORECASE)
        self.assertEqual(len(results), 2)  # one extra for listfilter

    def test_auth(self):
        group_updater = GroupUpdater(groups={})
        for codename in codenames:
            try:
                group_updater.get_from_dotted_codename(codename)
            except PermissionsCodenameError as e:
                self.fail(f"PermissionsCodenameError raised unexpectedly. Got {e}")
