from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase
from django.utils import timezone

from edc_timepoint.constants import OPEN_TIMEPOINT, CLOSED_TIMEPOINT
from edc_timepoint.model_mixins import TimepointStatusError

from example.models import ExampleModel


class TimepointStatusTests(TestCase):

    def setUp(self):
        ExampleModel.objects.create()

    def test_timepoint_status_open(self):
        example_model = ExampleModel.objects.create()
        self.assertEqual(example_model.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_open_date(self):
        app_config = django_apps.get_app_config('edc_timepoint')
        example_model = ExampleModel.objects.create()
        attrs = app_config.timepoint_models[example_model._meta.label_lower]
        datetime_field = attrs['datetime_field']
        self.assertEqual(example_model.timepoint_opened_datetime, getattr(example_model, datetime_field))

    def test_timepoint_status_close_fail(self):
        app_config = django_apps.get_app_config('edc_timepoint')
        example_model = ExampleModel.objects.create()
        attrs = app_config.timepoint_models[example_model._meta.label_lower]
        datetime_field = attrs['datetime_field']
        self.assertEqual(example_model.timepoint_opened_datetime, getattr(example_model, datetime_field))

    def test_timepoint_status_close_attempt(self):
        """Assert timepoint does not closed when tried."""
        example_model = ExampleModel.objects.create()
        example_model.close_timepoint()
        self.assertEqual(example_model.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_close_attempt2(self):
        """Assert timepoint closes because example_model status is "closed"."""
        example_model = ExampleModel.objects.create()
        example_model.example_status = 'finish'
        example_model.save()
        example_model.close_timepoint()
        self.assertRaises(TimepointStatusError, example_model.save)

    def test_timepoint_status_blocks(self):
        """Assert timepoint closes because example_model status is "closed" and blocks further changes."""
        example_model = ExampleModel.objects.create()
        example_model.example_status = 'finish'
        example_model.save()
        example_model.close_timepoint()
        self.assertRaises(TimepointStatusError, example_model.save)

    def test_timepoint_status_attrs(self):
        """Assert timepoint closes because example_model status is "finish" and blocks further changes."""
        example_model = ExampleModel.objects.create(report_datetime=timezone.now() - relativedelta(days=10))
        example_model.example_status = 'finish'
        example_model.save()
        example_model.close_timepoint()
        self.assertEqual(example_model.example_status, 'finish')
        self.assertEqual(example_model.timepoint_opened_datetime, example_model.report_datetime)
        self.assertGreater(example_model.timepoint_closed_datetime, example_model.timepoint_opened_datetime)
        self.assertEqual(example_model.timepoint_status, CLOSED_TIMEPOINT)
