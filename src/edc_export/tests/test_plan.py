import uuid

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..models import Plan
from .models import ListModel, SubjectVisit, Crf
from edc_export.model_exporter.plan_exporter import PlanExporter


app_config = django_apps.get_app_config('edc_export')


class TestPlan(TestCase):

    path = app_config.export_folder

    def setUp(self):
        self.thing_one = ListModel.objects.create(
            name='thing_one', short_name='thing_one')
        self.thing_two = ListModel.objects.create(
            name='thing_two', short_name='thing_two')
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier='12345',
            report_datetime=get_utcnow())
        self.crf = Crf.objects.create(
            subject_visit=self.subject_visit,
            char1='char',
            date1=get_utcnow(),
            int1=1,
            uuid1=uuid.uuid4())

    def test_plan(self):
        Plan.objects.create(
            name='test_plan',
            model='edc_export.crf')
        PlanExporter()
