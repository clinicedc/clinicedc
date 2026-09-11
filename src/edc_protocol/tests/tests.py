from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_protocol.trial_dates import trial_dates

opendte = datetime.now().astimezone(tz=ZoneInfo("UTC")) - relativedelta(years=2)
closedte = datetime.now().astimezone(tz=ZoneInfo("UTC")) + relativedelta(years=1)


@tag("protocol")
class TestProtocol(TestCase):
    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime.now().astimezone(tz=ZoneInfo("UTC"))
        - relativedelta(years=2),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime.now().astimezone(tz=ZoneInfo("UTC"))
        + relativedelta(years=1),
    )
    def test_protocol(self):
        self.assertEqual(trial_dates.study_open_datetime.date(), opendte.date())
        self.assertEqual(trial_dates.study_close_datetime.date(), closedte.date())
