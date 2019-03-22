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


User = get_user_model()


class ModelAdminSiteTest(WebTest):
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
            visit_models={"edc_appointment.appointment": "edc_model_admin.subjectvisit"}
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

    def test_redirect_next(self):
        """Assert redirects to "subject_dashboard_url" as give in the
        query_string "next=".
        """
        self.login()

        self.app.get(
            reverse(
                f"dashboard_app:subject_dashboard_url", args=(self.subject_identifier,)
            ),
            user=self.user,
            status=200,
        )

        CrfOne.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=self.subject_visit
        )

        model = "redirectnextmodel"
        query_string = (
            f"next=dashboard_app:subject_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )
        url = reverse(f"admin:edc_model_admin_{model}_add") + "?" + query_string

        response = self.app.get(url, user=self.user)
        response.form["subject_identifier"] = self.subject_identifier
        response = response.form.submit(name="_save").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    def test_redirect_save_next_crf(self):
        """Assert redirects CRFs for both add and change from
        crftwo -> crfthree -> dashboard.
        """
        self.login()

        self.app.get(
            reverse(
                f"dashboard_app:subject_dashboard_url", args=(self.subject_identifier,)
            ),
            user=self.user,
            status=200,
        )

        # add CRF Two
        model = "crftwo"
        query_string = (
            f"next=dashboard_app:subject_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )
        url = reverse(f"admin:edc_model_admin_{model}_add") + "?" + query_string

        # oops, cancel
        response = self.app.get(url, user=self.user)
        response = response.form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        # add CRF Two
        response = self.app.get(url, user=self.user)
        self.assertIn("Add crf two", response)
        response.form["subject_identifier"] = self.subject_identifier
        response.form["subject_visit"] = str(self.subject_visit.id)
        response = response.form.submit(name="_savenext").follow()

        # goes directly to CRF Three, add CRF Three
        self.assertIn("Add crf three", response)
        response.form["subject_identifier"] = self.subject_identifier
        response.form["subject_visit"] = str(self.subject_visit.id)
        response = response.form.submit(name="_savenext").follow()

        # goes to dashboard
        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

        crftwo = CrfTwo.objects.all()[0]

        url = (
            reverse(f"admin:edc_model_admin_{model}_change", args=(crftwo.id,))
            + "?"
            + query_string
        )

        response = self.app.get(url, user=self.user)
        response = response.form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        response = self.app.get(url, user=self.user)
        self.assertIn("Change crf two", response)
        response.form["subject_identifier"] = self.subject_identifier
        response.form["subject_visit"] = str(self.subject_visit.id)
        response = response.form.submit(name="_savenext").follow()

        self.assertIn("Change crf three", response)
        response.form["subject_identifier"] = self.subject_identifier
        response.form["subject_visit"] = str(self.subject_visit.id)
        response = response.form.submit(name="_savenext").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    def test_redirect_save_next_requisition(self):
        """Assert redirects requisitions for both add and change from
        panel one -> panel two -> dashboard.
        """
        self.login()

        self.app.get(
            reverse(
                f"dashboard_app:subject_dashboard_url", args=(self.subject_identifier,)
            ),
            user=self.user,
            status=200,
        )

        model = "requisition"
        query_string = (
            f"next=dashboard_app:subject_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}&"
            f"subject_visit={str(self.subject_visit.id)}"
        )

        panel_one = Panel.objects.get(name="one")
        panel_two = Panel.objects.get(name="two")
        url = reverse(f"admin:edc_model_admin_{model}_add")

        response = self.app.get(
            url + f"?{query_string}&panel={str(panel_one.id)}", user=self.user
        )
        response = response.form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        # add
        url = (
            reverse(f"admin:edc_model_admin_{model}_add")
            + f"?{query_string}&panel={str(panel_one.id)}"
        )
        response = self.app.get(url, user=self.user)
        self.assertIn("Add requisition", response)
        self.assertIn(f'value="{str(panel_one.id)}"', response)

        dte = get_utcnow()
        response.form["item_count"] = 1
        response.form["estimated_volume"] = 5
        response.form["is_drawn"] = YES
        response.form["drawn_datetime_0"] = dte.strftime("%Y-%m-%d")
        response.form["drawn_datetime_1"] = "12:00:00"
        response.form["clinic_verified"] = YES
        response.form["clinic_verified_datetime_0"] = dte.strftime("%Y-%m-%d")
        response.form["clinic_verified_datetime_1"] = "12:00:00"
        response = response.form.submit(name="_savenext").follow()

        url = (
            reverse(f"admin:edc_model_admin_{model}_add")
            + f"?{query_string}&panel={str(panel_two.id)}"
        )
        self.assertIn("Add requisition", response)
        self.assertIn(f'value="{str(panel_two.id)}"', response)
        dte = get_utcnow()
        response.form["item_count"] = 1
        response.form["estimated_volume"] = 5
        response.form["is_drawn"] = YES
        response.form["drawn_datetime_0"] = dte.strftime("%Y-%m-%d")
        response.form["drawn_datetime_1"] = "12:00:00"
        response.form["clinic_verified"] = YES
        response.form["clinic_verified_datetime_0"] = dte.strftime("%Y-%m-%d")
        response.form["clinic_verified_datetime_1"] = "12:00:00"
        response = response.form.submit(name="_savenext").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

        # change
        requisition = Requisition.objects.get(panel=panel_one)
        url = (
            reverse(f"admin:edc_model_admin_{model}_change", args=(requisition.id,))
            + f"?{query_string}&panel={str(panel_one.id)}"
        )
        response = self.app.get(url, user=self.user)
        self.assertIn("Change requisition", response)
        self.assertIn(f'{str(panel_one.id)}" selected>One</option>', response)
        response = response.form.submit(name="_savenext").follow()

        self.assertIn("Change requisition", response)
        self.assertIn(f'{str(panel_two.id)}" selected>Two</option>', response)
        self.assertIn(str(panel_two.id), response)
        response = response.form.submit(name="_savenext").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    def test_redirect_on_delete_with_url_name_from_settings(self):
        self.login()

        self.app.get(
            reverse(
                f"dashboard_app:subject_dashboard_url", args=(self.subject_identifier,)
            ),
            user=self.user,
            status=200,
        )

        model = "crffour"
        query_string = (
            f"next=dashboard_app:subject_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )
        url = reverse(f"admin:edc_model_admin_{model}_add") + "?" + query_string
        response = self.app.get(url, user=self.user)
        response.form["subject_identifier"] = self.subject_identifier
        response.form["subject_visit"] = str(self.subject_visit.id)
        response = response.form.submit(name="_save").follow()

        # delete
        crffour = CrfFour.objects.all()[0]
        url = (
            reverse(f"admin:edc_model_admin_{model}_change", args=(crffour.id,))
            + "?"
            + query_string
        )
        response = self.app.get(url, user=self.user)
        delete_url = reverse(
            f"admin:edc_model_admin_{model}_delete", args=(crffour.id,)
        )
        response = response.click(href=delete_url)

        # submit confirmation page
        response = response.form.submit().follow()

        # redirects to the dashboard
        self.assertIn("You are at the subject dashboard", response)
        self.assertRaises(ObjectDoesNotExist, CrfFour.objects.get, id=crffour.id)

    def test_redirect_on_delete_with_url_name_from_admin(self):
        self.login()

        crffive = CrfFive.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=self.subject_visit
        )

        model = "crffive"
        url = reverse(f"admin:edc_model_admin_{model}_change", args=(crffive.id,))
        response = self.app.get(url, user=self.user)
        delete_url = reverse(
            f"admin:edc_model_admin_{model}_delete", args=(crffive.id,)
        )
        response = response.click(href=delete_url)
        response = response.form.submit().follow()
        self.assertIn("You are at Dashboard Two", response)
        self.assertRaises(ObjectDoesNotExist, CrfFive.objects.get, id=crffive.id)

    def test_redirect_on_delete_with_url_name_is_none(self):
        self.login()

        crfsix = CrfSix.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=self.subject_visit
        )

        model = "crfsix"
        url = reverse(f"admin:edc_model_admin_{model}_change", args=(crfsix.id,))
        response = self.app.get(url, user=self.user)
        delete_url = reverse(f"admin:edc_model_admin_{model}_delete", args=(crfsix.id,))
        response = response.click(href=delete_url)
        response = response.form.submit().follow()
        self.assertRaises(ObjectDoesNotExist, CrfSix.objects.get, id=crfsix.id)
        self.assertIn("changelist", response)
