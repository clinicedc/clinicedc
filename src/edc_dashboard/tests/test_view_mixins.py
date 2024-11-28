from datetime import datetime
from zoneinfo import ZoneInfo

import arrow
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin, View
from edc_auth.auth_updater import AuthUpdater
from edc_auth.constants import CLINIC
from edc_auth.site_auths import site_auths
from edc_listboard.filters import ListboardFilter, ListboardViewFilters
from edc_listboard.view_mixins import ListboardFilterViewMixin, QueryStringViewMixin
from edc_listboard.views import ListboardView
from edc_registration.models import RegisteredSubject
from edc_sites.single_site import SingleSite
from edc_sites.site import sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_subject_dashboard.view_mixins import RegisteredSubjectViewMixin
from edc_test_utils.get_user_for_tests import get_user_for_tests
from edc_utils import get_utcnow
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from edc_dashboard.url_names import url_names

from .models import SubjectVisit


@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
    SITE_ID=101,
    EDC_SITES_REGISTER_DEFAULT=False,
)
class TestViewMixins(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        url_names.register("dashboard_url", "dashboard_url", "edc_dashboard")
        site_auths.clear()
        site_auths.add_group("edc_dashboard.view_my_listboard", name=CLINIC)
        site_auths.add_custom_permissions_tuples(
            model="edc_dashboard.edcpermissions",
            codename_tuples=(("edc_dashboard.view_my_listboard", "View my listboard"),),
        )
        AuthUpdater(verbose=False, warn_only=True)
        sites.initialize(initialize_site_model=True)
        single_site = SingleSite(
            101,
            "mochudi",
            title="Mochudi",
            country="botswana",
            country_code="bw",
            language_codes=["en"],
            domain="mochudi.bw.clinicedc.org",
        )
        sites.register(single_site)
        add_or_update_django_sites()
        rs = RegisteredSubject.objects.create(
            subject_identifier=f"{Site.objects.get_current().id}-123456-1"
        )
        cls.subject_identifier = rs.subject_identifier

    def setUp(self):
        self.user = get_user_for_tests(username="erik", view_only=True)
        group = Group.objects.get(name=CLINIC)
        self.user.groups.add(group)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

    def test_querystring_mixin(self):
        class MyView(QueryStringViewMixin, ContextMixin, View):
            pass

        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        self.assertIn("f=f", view.querystring)
        self.assertIn("e=e", view.querystring)
        self.assertIn("o=o", view.querystring)
        self.assertIn("q=q", view.querystring)
        for attr in ["f", "e", "o", "q"]:
            with self.subTest(attr=attr):
                self.assertEqual(attr, view.get_context_data().get(attr), attr)

    def test_listboard_filter_view(self):
        class MyListboardViewFilters(ListboardViewFilters):
            all = ListboardFilter(name="all", label="All", lookup={})

            scheduled = ListboardFilter(label="Scheduled", lookup={"reason": "scheduled"})

            not_scheduled = ListboardFilter(
                label="Not Scheduled",
                exclude_filter=True,
                lookup={"reason": "scheduled"},
            )

        class MyView(RegisteredSubjectViewMixin, ListboardFilterViewMixin, ListboardView):
            listboard_model = "edc_dashboard.subjectvisit"
            listboard_url = "listboard_url"
            listboard_template = "listboard_template"
            listboard_filter_url = "listboard_url"
            listboard_view_permission_codename = "edc_dashboard.view_my_listboard"
            listboard_view_filters = MyListboardViewFilters()

        start = datetime(2013, 5, 1, 12, 30, tzinfo=ZoneInfo("UTC"))
        end = datetime(2013, 5, 10, 17, 15, tzinfo=ZoneInfo("UTC"))
        for arr in arrow.Arrow.range("day", start, end):
            SubjectVisit.objects.create(
                subject_identifier=self.subject_identifier,
                report_datetime=arr.datetime,
                reason=MISSED_VISIT,
                user_created=self.user.username,
            )
        subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            reason=SCHEDULED,
            user_created=self.user.username,
        )
        request = RequestFactory().get("/?scheduled=scheduled")
        request.user = self.user
        request.site = Site.objects.get_current()
        request.template_data = {"listboard_template": "listboard.html"}
        template_response = MyView.as_view()(
            request=request, subject_identifier=self.subject_identifier
        )
        object_list = template_response.__dict__.get("context_data").get("object_list")
        self.assertEqual(
            [obj.reason for obj in object_list if obj.pk == subject_visit.pk],
            [subject_visit.reason],
        )
