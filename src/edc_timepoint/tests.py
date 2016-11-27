from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase

from edc_base.utils import get_utcnow
from edc_timepoint.constants import OPEN_TIMEPOINT, CLOSED_TIMEPOINT
from edc_timepoint.model_mixins import TimepointError

from example.models import ExampleModel, CrfModel, Visit


class TimepointTests(TestCase):

    def setUp(self):
        ExampleModel.objects.create()

    def test_timepoint_status_open(self):
        example_model = ExampleModel.objects.create()
        self.assertEqual(example_model.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_open_date(self):
        app_config = django_apps.get_app_config('edc_timepoint')
        example_model = ExampleModel.objects.create()
        timepoint = app_config.timepoints[example_model._meta.label_lower]
        self.assertEqual(example_model.timepoint_opened_datetime, getattr(example_model, timepoint.datetime_field))

    def test_timepoint_status_close_fail(self):
        app_config = django_apps.get_app_config('edc_timepoint')
        example_model = ExampleModel.objects.create()
        timepoint = app_config.timepoints[example_model._meta.label_lower]
        self.assertEqual(example_model.timepoint_opened_datetime, getattr(example_model, timepoint.datetime_field))

    def test_timepoint_status_close_attempt(self):
        """Assert timepoint does not closed when tried."""
        example_model = ExampleModel.objects.create()
        example_model.timepoint_close_timepoint()
        self.assertEqual(example_model.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_close_attempt2(self):
        """Assert timepoint closes because example_model status is "closed"."""
        example_model = ExampleModel.objects.create()
        example_model.example_status = 'finish'
        example_model.save()
        example_model.timepoint_close_timepoint()
        self.assertRaises(TimepointError, example_model.save)

    def test_timepoint_status_blocks(self):
        """Assert timepoint closes because example_model status is "closed" and blocks further changes."""
        example_model = ExampleModel.objects.create()
        example_model.example_status = 'finish'
        example_model.save()
        example_model.timepoint_close_timepoint()
        self.assertRaises(TimepointError, example_model.save)

    def test_timepoint_status_attrs(self):
        """Assert timepoint closes because example_model status is "finish" and blocks further changes."""
        example_model = ExampleModel.objects.create(report_datetime=get_utcnow() - relativedelta(days=10))
        example_model.example_status = 'finish'
        example_model.save()
        example_model.timepoint_close_timepoint()
        self.assertEqual(example_model.example_status, 'finish')
        self.assertEqual(example_model.timepoint_opened_datetime, example_model.report_datetime)
        self.assertGreater(example_model.timepoint_closed_datetime, example_model.timepoint_opened_datetime)
        self.assertEqual(example_model.timepoint_status, CLOSED_TIMEPOINT)

    def test_timepoint_lookup_blocks_create(self):
        example_model = ExampleModel.objects.create(report_datetime=get_utcnow() - relativedelta(days=10))
        example_model.example_status = 'finish'
        example_model.save()
        visit = Visit.objects.create(example_model=example_model)
        example_model.timepoint_close_timepoint()
        self.assertRaises(TimepointError, CrfModel.objects.create, visit=visit)

    def test_timepoint_lookup_blocks_update(self):
        example_model = ExampleModel.objects.create(report_datetime=get_utcnow() - relativedelta(days=10))
        example_model.example_status = 'finish'
        example_model.save()
        visit = Visit.objects.create(example_model=example_model)
        crf_model = CrfModel.objects.create(visit=visit)
        example_model.timepoint_close_timepoint()
        self.assertRaises(TimepointError, crf_model.save)
