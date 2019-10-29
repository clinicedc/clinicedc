import uuid

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_utils import get_utcnow

from ..models import Plan
from ..model_exporter import PlanExporter
from .models import ListModel, SubjectVisit, Crf


app_config = django_apps.get_app_config("edc_export")


class TestPlan(TestCase):

    path = app_config.export_folder

    def setUp(self):
        self.thing_one = ListModel.objects.create(
            display_name="thing_one", name="thing_one"
        )
        self.thing_two = ListModel.objects.create(
            display_name="thing_two", name="thing_two"
        )
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier="12345", report_datetime=get_utcnow()
        )
        self.crf = Crf.objects.create(
            subject_visit=self.subject_visit,
            char1="char",
            date1=get_utcnow(),
            int1=1,
            uuid1=uuid.uuid4(),
        )

    def test_plan(self):
        plan_name = "test_plan"
        Plan.objects.create(name=plan_name, model="edc_export.crf")
        PlanExporter(plan_name=plan_name)
