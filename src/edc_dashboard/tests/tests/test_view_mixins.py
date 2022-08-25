from datetime import datetime
from zoneinfo import ZoneInfo

import arrow
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin, View
from edc_auth.auth_objects import CLINIC
from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths
from edc_listboard.filters import ListboardFilter, ListboardViewFilters
from edc_listboard.view_mixins import ListboardFilterViewMixin, QueryStringViewMixin
from edc_listboard.views import ListboardView
from edc_model_wrapper import ModelWrapper
from edc_utils import get_utcnow

from edc_dashboard.url_names import url_names

from ..models import SubjectVisit


@override_settings(EDC_AUTH_SKIP_SITE_AUTHS=True, EDC_AUTH_SKIP_AUTH_UPDATER=False)
class TestViewMixins(TestCase):
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
        return super().setUpTestData()

    def setUp(self):
        self.user = User.objects.create(username="erik")
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
        class SubjectVisitModelWrapper(ModelWrapper):
            model = "edc_dashboard.subjectvisit"
            next_url_name = "dashboard_url"

        class MyListboardViewFilters(ListboardViewFilters):
            all = ListboardFilter(name="all", label="All", lookup={})

            scheduled = ListboardFilter(label="Scheduled", lookup={"reason": "scheduled"})

            not_scheduled = ListboardFilter(
                label="Not Scheduled",
                exclude_filter=True,
                lookup={"reason": "scheduled"},
            )

        class MyView(ListboardFilterViewMixin, ListboardView):
            listboard_model = "edc_dashboard.subjectvisit"
            listboard_url = "listboard_url"
            listboard_template = "listboard_template"
            listboard_filter_url = "listboard_url"
            listboard_view_permission_codename = "edc_dashboard.view_my_listboard"
            model_wrapper_cls = SubjectVisitModelWrapper
            listboard_view_filters = MyListboardViewFilters()

        start = datetime(2013, 5, 1, 12, 30, tzinfo=ZoneInfo("UTC"))
        end = datetime(2013, 5, 10, 17, 15, tzinfo=ZoneInfo("UTC"))
        for arr in arrow.Arrow.range("day", start, end):
            SubjectVisit.objects.create(
                subject_identifier="1234", report_datetime=arr.datetime, reason="missed"
            )
        subject_visit = SubjectVisit.objects.create(
            subject_identifier="1234", report_datetime=get_utcnow(), reason="scheduled"
        )
        request = RequestFactory().get("/?scheduled=scheduled")
        request.user = self.user
        request.site = Site.objects.get_current()
        request.template_data = {"listboard_template": "listboard.html"}
        template_response = MyView.as_view()(request=request)
        object_list = template_response.__dict__.get("context_data").get("object_list")
        self.assertEqual(
            [
                wrapper.object.reason
                for wrapper in object_list
                if wrapper.object.pk == subject_visit.pk
            ],
            [subject_visit.reason],
        )
