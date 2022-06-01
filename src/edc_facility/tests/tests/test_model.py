from django.test import TestCase
from edc_utils import get_utcnow

from ...models import Holiday


class TestModel(TestCase):
    def test_str(self):
        obj = Holiday.objects.create(
            country="botswana", local_date=get_utcnow().date(), name="holiday"
        )
        self.assertTrue(str(obj))
