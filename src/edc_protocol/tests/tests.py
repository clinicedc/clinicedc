from pprint import pprint

from dateutil.relativedelta import relativedelta
from django.test import override_settings, TestCase, tag
from edc_protocol import Protocol
from edc_utils import get_utcnow

opendte = get_utcnow() - relativedelta(years=2)
closedte = get_utcnow() + relativedelta(years=1)


class TestProtocol(TestCase):
    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=2),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    )
    def test_protocol(self):
        self.assertEqual(Protocol().study_open_datetime.date(), opendte.date())
        self.assertEqual(Protocol().study_close_datetime.date(), closedte.date())
