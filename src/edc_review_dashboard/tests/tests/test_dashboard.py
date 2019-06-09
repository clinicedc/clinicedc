from dashboard_app.lab_profiles import lab_profile
from dashboard_app.models import Appointment, SubjectVisit, SubjectConsent
from dashboard_app.reference_configs import register_to_site_reference_configs
from dashboard_app.visit_schedule import visit_schedule
from django.contrib.auth import get_user_model
from django.test import tag  # noqa
from django.urls.base import reverse
from django_webtest import WebTest
from edc_facility.import_holidays import import_holidays
from edc_lab.site_labs import site_labs
from edc_reference.site_reference import site_reference_configs
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from dateutil.relativedelta import relativedelta

User = get_user_model()

"""
subject_dashboard_url
subject_review_listboard_url
requisition_print_actions_url
requisition_verify_actions_url
"""


class TestDashboard(WebTest):
    @classmethod
    def setUpClass(cls):
        ret = super().setUpClass()
        import_holidays()
        return ret

    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "dashboard_app.subjectvisit"}
        )

        self.subject_identifier = "092-40990029-4"
        identity = "123456789"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow(),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                appointment = Appointment.objects.create(
                    appt_datetime=get_utcnow(),
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name="visit_schedule",
                    schedule_name="schedule",
                    visit_code=visit.code,
                    user_created="user_login",
                )
                SubjectVisit.objects.create(
                    appointment=appointment,
                    subject_identifier=self.subject_identifier,
                    reason=SCHEDULED,
                    user_created="user_login",
                )
        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "dashboard_app.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    def login(self):
        form = self.app.get(reverse("admin:index")).maybe_follow().form
        form["username"] = self.user.username
        form["password"] = "pass"
        return form.submit()

    def test_url(self):
        self.login()

        response = self.app.get(
            reverse(f"dashboard_app:subject_review_listboard_url"),
            user=self.user,
            status=200,
        )

        n = SubjectVisit.objects.all().count()
        self.assertIn("Subjects", response.html.get_text())

        # shows something like 1. 12345 3 visits
        self.assertIn(f"{self.subject_identifier} {n} visits", response.html.get_text())
        self.assertIn("click to list reported visits for this subject", response)

        # follow to schedule for this subject
        response = response.click(linkid="id-reported-visit-list")
        self.assertIn(
            f"Subject Review: Reported visits for {self.subject_identifier}",
            response.html.get_text(),
        )
        self.assertIn("1000.0", response.html.get_text())
        self.assertIn("2000.0", response.html.get_text())
        self.assertIn("3000.0", response.html.get_text())

        response = response.click(
            linkid=f"id-reported-visits-{self.subject_identifier}-1000-0"
        )

        # print(response.html.get_text())
        # follow to dashoard for this visit
        # response = response.click(linkid="id-reported-visit-list")

    def test_url_response_for_subject_identifier(self):
        self.login()

        response = self.app.get(
            reverse(
                f"dashboard_app:subject_review_listboard_url",
                kwargs={"subject_identifier": self.subject_identifier},
            ),
            user=self.user,
        )

        # print(response.html.get_text())

        self.assertIn("id-reported-visit-list", response)
        self.assertIn(self.subject_identifier, response)

        response = response.click(linkid="id-reported-visit-list")

    #         for link in response.html.find_all('a'):
    #             print(link.get('href'))
    #         print(response.html.get_text())

    def test_url_response_for_subject_identifier_to_dashboard(self):
        self.login()

        response = self.app.get(
            reverse(
                f"dashboard_app:subject_review_listboard_url",
                kwargs={"subject_identifier": self.subject_identifier},
            ),
            user=self.user,
        )
        response = response.click(linkid="id-reported-visit-list")
