from datetime import datetime
from unittest import skip
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_constants import YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import (
    CrfFive,
    CrfFour,
    CrfOne,
    CrfThree,
    CrfTwo,
    SubjectRequisition,
)
from clinicedc_tests.utils import get_webtest_form
from clinicedc_tests.visit_schedules.visit_schedule_dashboard.visit_schedule import (
    get_visit_schedule,
)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings, tag
from django.urls.base import reverse
from django.utils import timezone
from django_webtest import WebTest

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_lab.tests import SiteLabsTestHelper
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

User = get_user_model()


utc_tz = ZoneInfo("UTC")


@tag("model_admin")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class ModelAdminSiteTest(WebTest):
    lab_helper = SiteLabsTestHelper()
    csrf_checks = False

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        self.user.userprofile.sites.add(Site.objects.get(id=10))

        self.helper = Helper()
        self.subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
            report_datetime=timezone.now() - relativedelta(days=1),
        )
        self.subject_identifier = self.subject_visit.subject_identifier

    def login(self):
        response = self.app.get(reverse("admin:index")).maybe_follow()
        for form in response.forms.values():
            if form.action == "/i18n/setlang/":
                # exclude the locale form
                continue
            break
        form["username"] = self.user.username
        form["password"] = "pass"  # noqa: S105
        return form.submit()

    def test_redirect_next(self):
        """Assert redirects to "dashboard_url" as given in the
        query_string "next=".
        """
        self.login()

        self.app.get(
            reverse("clinicedc_tests:test_dashboard_url", args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )

        CrfOne.objects.create(subject_visit=self.subject_visit, report_datetime=timezone.now())

        model = "redirectnextmodel"
        query_string = (
            "next=clinicedc_tests:test_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )

        url = (
            reverse(f"clinicedc_tests_admin:clinicedc_tests_{model}_add") + "?" + query_string
        )

        response = self.app.get(url, user=self.user)
        form = get_webtest_form(response)
        form["subject_identifier"] = self.subject_identifier
        response = form.submit(name="_save").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    @skip("FIXME")
    def test_redirect_save_next_crf(self):
        """Assert redirects CRFs for both add and change from
        crffour -> crffive -> dashboard.
        """
        self.login()

        self.app.get(
            reverse("clinicedc_tests:test_dashboard_url", args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )

        # add CRF Four
        model = "crffour"
        query_string = (
            "next=clinicedc_tests:test_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )
        url = (
            reverse(f"clinicedc_tests_admin:clinicedc_tests_{model}_add") + "?" + query_string
        )

        # oops, cancel
        response = self.app.get(url, user=self.user)
        self.assertIn("Add crf four", response)
        form = get_webtest_form(response)
        response = form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        # add CRF four
        response = self.app.get(url, user=self.user)
        self.assertIn("Add crf four", response)
        form_data = {
            # "subject_visit": str(self.subject_visit.id),
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        response = form.submit(name="_savenext").follow()

        # goes directly to CRF Three, add CRF five
        self.assertIn("Add crf five", response)
        form_data = {
            "subject_visit": str(self.subject_visit.id),
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        response = form.submit(name="_savenext").follow()

        # goes to dashboard
        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

        crftwo = CrfTwo.objects.all()[0]
        url = reverse(
            "clinicedc_tests_admin:clinicedc_tests_crffour_change", args=(crftwo.id,)
        )
        url = url + "?" + query_string

        response = self.app.get(url, user=self.user)
        form = get_webtest_form(response)
        response = form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        response = self.app.get(url, user=self.user)
        self.assertIn("crffour change-form", response)
        form_data = {
            "subject_visit": str(self.subject_visit.id),
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        response = form.submit(name="_savenext").follow()

        # skips over crffive to crffour, since crffive
        # has been entered already
        self.assertIn("crffour change-form", response)

        crfthree = CrfThree.objects.all()[0]
        url = reverse(
            "clinicedc_tests_admin:clinicedc_tests_crffour_change", args=(crfthree.id,)
        )
        url = url + "?" + query_string

        response = self.app.get(url, user=self.user)
        self.assertIn("crffour change-form", response)

        form_data = {
            "subject_visit": str(self.subject_visit.id),
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        response = form.submit(name="_savenext").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    @skip("FIXME")
    def test_redirect_save_next_requisition(self):  # noqa: PLR0915
        """Assert redirects requisitions for both add and change from
        panel one -> panel two -> dashboard.
        """
        self.login()

        self.app.get(
            reverse("clinicedc_tests:test_dashboard_url", args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )

        model = "requisition"
        query_string = (
            "next=clinicedc_tests:test_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}&"
            f"subject_visit={self.subject_visit.id!s}"
        )

        panel_one = Panel.objects.get(name="one")
        panel_two = Panel.objects.get(name="two")

        # got to add and cancel
        add_url = reverse(f"clinicedc_tests_admin:clinicedc_tests_{model}_add")
        url = add_url + f"?{query_string}&panel={panel_one.id!s}"
        response = self.app.get(url, user=self.user)
        form = get_webtest_form(response)
        response = form.submit(name="_cancel").follow()
        self.assertIn("You are at the subject dashboard", response)

        dte = timezone.now()
        form_data = {
            "item_count": 1,
            "estimated_volume": 5,
            "is_drawn": YES,
            "drawn_datetime_0": dte.strftime("%Y-%m-%d"),
            "drawn_datetime_1": "00:00:00",
            "clinic_verified": YES,
            "clinic_verified_datetime_0": dte.strftime("%Y-%m-%d"),
            "clinic_verified_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }

        # add and save
        url = add_url + f"?{query_string}&panel={panel_one.id!s}"
        response = self.app.get(url, user=self.user)
        self.assertIn("Add requisition", response)
        self.assertIn(f'value="{panel_one.id!s}"', response)
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        form["requisition_identifier"] = "ABCDE0001"
        response = form.submit().follow()
        self.assertIn("You are at the subject dashboard", response)
        SubjectRequisition.objects.all().delete()

        # add panel one and save_next ->
        # add panel two and save_next -> dashboard
        url = add_url + f"?{query_string}&panel={panel_one.id!s}"
        response = self.app.get(url, user=self.user)
        self.assertIn("Add requisition", response)
        self.assertIn(f'value="{panel_one.id!s}"', response)
        self.assertIn("_savenext", response)
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        form["requisition_identifier"] = "ABCDE0001"
        response = form.submit(name="_savenext").follow()
        self.assertIn("Add requisition", response)
        self.assertIn(f'value="{panel_two.id!s}"', response)
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        form["requisition_identifier"] = "ABCDE0002"
        response = form.submit(name="_savenext").follow()
        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

        # change panel one and save_next -> change panel two and save_next ->
        # dashboard
        requisition = SubjectRequisition.objects.get(requisition_identifier="ABCDE0001")
        url = (
            reverse(
                f"clinicedc_tests_admin:clinicedc_tests_{model}_change",
                args=(requisition.id,),
            )
            + f"?{query_string}&panel={panel_one.id!s}"
        )
        response = self.app.get(url, user=self.user)
        self.assertIn("requisition change-form", response)
        self.assertIn("ABCDE0001", response)
        self.assertIn(f'{panel_one.id!s}" selected>One</option>', response)
        form = get_webtest_form(response)
        response = form.submit(name="_savenext").follow()

        self.assertIn("You are at the subject dashboard", response)
        self.assertIn(self.subject_identifier, response)

    @skip("FIXME")
    def test_redirect_on_delete_with_url_name_from_settings(self):
        self.login()

        self.app.get(
            reverse("clinicedc_tests:test_dashboard_url", args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )

        model = "crffour"
        query_string = (
            "next=clinicedc_tests:test_dashboard_url,subject_identifier&"
            f"subject_identifier={self.subject_identifier}"
        )
        url = (
            reverse(f"clinicedc_tests_admin:clinicedc_tests_{model}_add") + "?" + query_string
        )

        form_data = {
            "subject_visit": str(self.subject_visit.id),
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        response = self.app.get(url, user=self.user)
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        form.submit(name="_save").follow()

        # delete
        crffour = CrfFour.objects.all()[0]
        url = (
            reverse(
                f"clinicedc_tests_admin:clinicedc_tests_{model}_change",
                args=(crffour.id,),
            )
            + "?"
            + query_string
        )
        response = self.app.get(url, user=self.user)
        delete_url = reverse(
            f"clinicedc_tests_admin:clinicedc_tests_{model}_delete", args=(crffour.id,)
        )
        response = response.click(href=delete_url)

        # submit confirmation page
        form = get_webtest_form(response)
        response = form.submit().follow()

        # redirects to the dashboard
        self.assertIn("You are at the subject dashboard", response)
        self.assertRaises(ObjectDoesNotExist, CrfFour.objects.get, id=crffour.id)

    @skip("FIXME")
    def test_redirect_on_delete_with_url_name_from_admin(self):
        self.login()

        crffive = CrfFive.objects.create(
            subject_visit=self.subject_visit, report_datetime=timezone.now()
        )

        model = "crffive"
        url = reverse(
            f"clinicedc_tests_admin:clinicedc_tests_{model}_change", args=(crffive.id,)
        )
        response = self.app.get(url, user=self.user)
        delete_url = reverse(
            f"clinicedc_tests_admin:clinicedc_tests_{model}_delete", args=(crffive.id,)
        )
        response = response.click(href=delete_url)
        form = get_webtest_form(response)
        response = form.submit().follow()
        self.assertIn("You are at Dashboard Two", response)
        self.assertRaises(ObjectDoesNotExist, CrfFive.objects.get, id=crffive.id)

    @skip("FIXME")
    def test_redirect_on_delete_with_url_name_is_none(self):
        self.login()

        crffour = CrfFour.objects.create(
            subject_visit=self.subject_visit, report_datetime=timezone.now()
        )

        model = "crffour"
        url = reverse(
            f"clinicedc_tests_admin:clinicedc_tests_{model}_change", args=(crffour.id,)
        )
        response = self.app.get(url, user=self.user)
        delete_url = reverse(
            f"clinicedc_tests_admin:clinicedc_tests_{model}_delete", args=(crffour.id,)
        )
        response = response.click(href=delete_url)
        form = get_webtest_form(response)
        response = form.submit().follow()
        self.assertRaises(ObjectDoesNotExist, CrfFour.objects.get, id=crffour.id)
        self.assertIn("changelist", response)

    def test_add_directly_from_changelist_without_subject_visit_raises(self):
        self.login()

        self.app.get(
            reverse("clinicedc_tests:test_dashboard_url", args=(self.subject_identifier,)),
            user=self.user,
            status=200,
        )

        model = "crfseven"
        add_url = reverse(f"clinicedc_tests_admin:clinicedc_tests_{model}_add")

        form_data = {
            "report_datetime_0": timezone.now().strftime("%Y-%m-%d"),
            "report_datetime_1": "00:00:00",
            "site": Site.objects.get(id=settings.SITE_ID).id,
        }
        response = self.app.get(add_url, user=self.user)
        form = get_webtest_form(response)
        for key, value in form_data.items():
            form[key] = value
        try:
            form.submit(name="_savenext").follow()
        except AssertionError:
            response = form.submit(name="_savenext")
        self.assertIn("This field is required", response)
