import arrow

from datetime import datetime
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin, View
from edc_base.utils import get_utcnow
from edc_dashboard.tests.models import SubjectVisit
from edc_dashboard.view_mixins.listboard.querystring_view_mixin import QueryStringViewMixin
from edc_model_wrapper import ModelWrapper

from ..listboard_filter import ListboardFilter, ListboardViewFilters
from ..view_mixins import ListboardFilterViewMixin
from ..views import ListboardView
from pprint import pprint


class TestViewMixins(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = 'erik'

    @tag('1')
    def test_querystring_mixin(self):

        class MyView(QueryStringViewMixin, ContextMixin, View):
            pass

        request = RequestFactory().get('/?f=f&e=e&o=o&q=q')
        request.user = 'erik'
        view = MyView(request=request)
        self.assertIn('f=f', view.querystring)
        self.assertIn('e=e', view.querystring)
        self.assertIn('o=o', view.querystring)
        self.assertIn('q=q', view.querystring)
        for attr in ['f', 'e', 'o', 'q']:
            with self.subTest(attr=attr):
                self.assertEqual(attr, view.get_context_data().get(attr), attr)

    @tag('1')
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

            model = 'edc_dashboard.subjectvisit'
            listboard_url = 'listboard_url'
            listboard_template = 'listboard_template'
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
        request.user = 'erik'
        request.url_name_data = {'listboard_url': 'listboard_url'}
        request.template_data = {'listboard_template': 'listboard.html'}
        template_response = MyView.as_view()(request=request)
        object_list = template_response.__dict__.get(
            'context_data').get('object_list')
        self.assertEqual(
            [wrapper.object.reason for wrapper in object_list], [subject_visit.reason])
