from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import tag
from django.urls.base import reverse
from django_webtest import WebTest
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_lab.site_labs import site_labs
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from review_dashboard_app.lab_profiles import lab_profile
from review_dashboard_app.models import SubjectConsent
from review_dashboard_app.reference_configs import register_to_site_reference_configs
from review_dashboard_app.visit_schedule import visit_schedule

User = get_user_model()


class TestDashboard(WebTest):
    @classmethod
    def setUpClass(cls):
        ret = super().setUpClass()
        import_holidays()
        return ret

    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.user.refresh_from_db()
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        register_to_site_reference_configs()

        self.subject_identifiers = ["101-40990028-3", "101-40990029-4"]

        for subject_identifier in self.subject_identifiers:
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=subject_identifier,
                consent_datetime=get_utcnow() - relativedelta(days=10),
                identity=subject_identifier,
                confirm_identity=subject_identifier,
                dob=get_utcnow() - relativedelta(years=25),
            )

            # put subject on schedule
            _, schedule = site_visit_schedules.get_by_onschedule_model(
                "review_dashboard_app.onschedule"
            )
            schedule.put_on_schedule(
                subject_identifier=subject_consent.subject_identifier,
                onschedule_datetime=subject_consent.consent_datetime,
            )
            for appointment in Appointment.objects.filter(
                subject_identifier=subject_identifier
            ).order_by("appt_datetime"):
                SubjectVisit.objects.create(
                    appointment=appointment,
                    report_datetime=appointment.appt_datetime,
                    subject_identifier=subject_identifier,
                    reason=SCHEDULED,
                    visit_code=appointment.visit_code,
                    visit_code_sequence=appointment.visit_code_sequence,
                    visit_schedule_name=appointment.visit_schedule_name,
                    schedule_name=appointment.schedule_name,
                    user_created="user_login",
                )
                appointment.appt_status = INCOMPLETE_APPT
                appointment.save()

    def login(self):
        form = self.app.get(reverse("admin:index")).maybe_follow().form
        form["username"] = self.user.username
        form["password"] = "pass"  # nosec B105
        return form.submit()

    def test_url(self):
        self.login()

        response = self.app.get(
            reverse("review_dashboard_app:subject_review_listboard_url"),
            user=self.user,
            status=200,
        )

        n = SubjectVisit.objects.filter(subject_identifier=self.subject_identifiers[1]).count()
        self.assertIn("Subjects", response.html.get_text())

        # shows something like 1. 12345 3 visits
        self.assertIn(f"{self.subject_identifiers[1]} {n} visits", response.html.get_text())
        self.assertIn("click to list reported visits for this subject", response)

        # follow to schedule for this subject
        response = response.click(
            linkid=f"id-reported-visit-list-{self.subject_identifiers[1]}"
        )
        self.assertIn(
            f"Subject Review: Reported visits for {self.subject_identifiers[1]}",
            response.html.get_text(),
        )
        self.assertIn("1000.0", response.html.get_text())
        self.assertIn("2000.0", response.html.get_text())
        self.assertIn("3000.0", response.html.get_text())

        # response = response.click(
        #     linkid=f"id-reported-visits-{self.subject_identifiers[1]}-1000-0"
        # )

        # print(response.html.get_text())
        # follow to dashoard for this visit
        # response = response.click(linkid="id-reported-visit-list")

    @tag("1")
    def test_url_response_for_subject_identifier(self):
        self.login()

        response = self.app.get(
            reverse(
                "review_dashboard_app:subject_review_listboard_url",
                kwargs={"subject_identifier": self.subject_identifiers[1]},
            ),
            user=self.user,
        )

        self.assertIn(f"id-reported-visits-{self.subject_identifiers[1]}", response)

        self.assertIn(self.subject_identifiers[1], response)

    def test_ordering(self):
        self.login()

        response = self.app.get(
            reverse("review_dashboard_app:subject_review_listboard_url"),
            user=self.user,
        )
        # response = response.click(linkid="id-reported-visit-list")
        self.assertIn(f"1. {self.subject_identifiers[1]}", response.html.get_text())
        self.assertIn(f"2. {self.subject_identifiers[0]}", response.html.get_text())
