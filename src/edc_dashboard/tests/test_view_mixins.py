import arrow

from datetime import datetime
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin, View
from edc_base.utils import get_utcnow
from edc_model_wrapper import ModelWrapper
from edc_permissions.permissions_updater import AUDITOR, ADMINISTRATION, LAB, PHARMACY
from edc_permissions.permissions_updater import PermissionsUpdater, CLINIC

from ..listboard_filter import ListboardFilter, ListboardViewFilters
from ..view_mixins import ListboardFilterViewMixin
from ..view_mixins.listboard.querystring_view_mixin import QueryStringViewMixin
from ..views import ListboardView
from .models import SubjectVisit


class TestViewMixins(TestCase):

    def setUp(self):
        class MyPermissionsUpdater(PermissionsUpdater):
            default_auditor_app_labels = []
            default_pii_models = []
            navbar_codenames = {
                ADMINISTRATION: [],
                AUDITOR: [],
                CLINIC: [],
                LAB: [],
                PHARMACY: []}

            extra_dashboard_codenames = {
                'blah': [
                    ('view_my_listboard', 'View my listboard')]}

            def extra_clinic_group_permissions(self, group):
                for permission in Permission.objects.filter(content_type__app_label__in=[
                        'edc_dashboard']):
                    group.permissions.add(permission)

        MyPermissionsUpdater()
        self.user = User.objects.create(username='erik')
        group = Group.objects.get(name=CLINIC)
        self.user.groups.add(group)
        self.request = RequestFactory().get('/')
        self.request.user = self.user

    def test_querystring_mixin(self):

        class MyView(QueryStringViewMixin, ContextMixin, View):
            pass

        request = RequestFactory().get('/?f=f&e=e&o=o&q=q')
        request.user = self.user
        view = MyView(request=request)
        self.assertIn('f=f', view.querystring)
        self.assertIn('e=e', view.querystring)
        self.assertIn('o=o', view.querystring)
        self.assertIn('q=q', view.querystring)
        for attr in ['f', 'e', 'o', 'q']:
            with self.subTest(attr=attr):
                self.assertEqual(attr, view.get_context_data().get(attr), attr)

    def test_listboard_filter_view(self):

        class SubjectVisitModelWrapper(ModelWrapper):
            model = 'edc_dashboard.subjectvisit'
            next_url_name = 'thenexturl'

        class MyListboardViewFilters(ListboardViewFilters):

            all = ListboardFilter(
                name='all',
                label='All',
                lookup={})

            scheduled = ListboardFilter(
                label='Scheduled',
                lookup={'reason': 'scheduled'})

            not_scheduled = ListboardFilter(
                label='Not Scheduled',
                exclude_filter=True,
                lookup={'reason': 'scheduled'})

        class MyView(ListboardFilterViewMixin, ListboardView):

            listboard_model = 'edc_dashboard.subjectvisit'
            listboard_url = 'listboard_url'
            listboard_template = 'listboard_template'
            listboard_filter_url = 'listboard_url'
            listboard_view_permission_codename = 'edc_dashboard.view_my_listboard'
            model_wrapper_cls = SubjectVisitModelWrapper
            listboard_view_filters = MyListboardViewFilters()

        start = datetime(2013, 5, 1, 12, 30)
        end = datetime(2013, 5, 10, 17, 15)
        for r in arrow.Arrow.range('day', start, end):
            SubjectVisit.objects.create(
                subject_identifier='1234',
                report_datetime=r.datetime,
                reason='missed')
        subject_visit = SubjectVisit.objects.create(
            subject_identifier='1234',
            report_datetime=get_utcnow(),
            reason='scheduled')
        request = RequestFactory().get('/?scheduled=scheduled')
        request.user = self.user
        request.site = Site.objects.get_current()
        request.url_name_data = {'listboard_url': 'listboard_url'}
        request.template_data = {'listboard_template': 'listboard.html'}
        template_response = MyView.as_view()(request=request)
        object_list = template_response.__dict__.get(
            'context_data').get('object_list')
        self.assertEqual(
            [wrapper.object.reason for wrapper in object_list
             if wrapper.object.pk == subject_visit.pk], [subject_visit.reason])
