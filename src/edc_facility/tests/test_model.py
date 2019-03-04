from django.test import TestCase, tag
from edc_facility.models import Holiday
from edc_utils import get_utcnow


class TestModel(TestCase):
    def test_str(self):
        obj = Holiday.objects.create(
            country="botswana", local_date=get_utcnow().date(), name="holiday"
        )
        self.assertTrue(str(obj))
