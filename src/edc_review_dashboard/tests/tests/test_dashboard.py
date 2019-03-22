from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import tag  # noqa
from django.urls.base import reverse
from django_webtest import WebTest
from edc_constants.constants import YES
from edc_lab.models.panel import Panel
from edc_lab.site_labs import site_labs
from edc_reference.site import site_reference_configs
from edc_utils.date import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..lab_profiles import lab_profile
from ..models import (
    Appointment,
    SubjectVisit,
    CrfOne,
    CrfTwo,
    CrfFour,
    CrfFive,
    CrfSix,
    Requisition,
)
from ..reference_configs import register_to_site_reference_configs
from ..visit_schedule import visit_schedule
from pprint import pprint
from django.conf import settings

User = get_user_model()


class TestDashboard(WebTest):

    def setUp(self):
        self.user = User.objects.create_superuser(
            "user_login", "u@example.com", "pass")

        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "edc_model_admin.subjectvisit"}
        )

        self.subject_identifier = "12345"
        self.appointment = Appointment.objects.create(
            appt_datetime=get_utcnow(),
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code="1000",
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

    def login(self):
        form = self.app.get(reverse("admin:index")).maybe_follow().form
        form["username"] = self.user.username
        form["password"] = "pass"
        return form.submit()

    def test_(self):
        self.login()

        self.app.get(
            reverse(f"dashboard_app:subject_review_listboard_url",
                    args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )
