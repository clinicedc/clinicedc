from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_utils.date import get_utcnow

from edc_refusal.forms import SubjectRefusalForm
from edc_refusal.models import RefusalReasons, SubjectRefusal

from ..models import SubjectScreening


class TestForms(TestCase):
    def get_data(self):
        refusal_reason = RefusalReasons.objects.all()[0]
        return {
            "screening_identifier": "12345",
            "report_datetime": get_utcnow(),
            "reason": refusal_reason,
            "other_reason": None,
            "comment": None,
        }

    def test_subject_refusal_ok(self):

        SubjectScreening.objects.create(
            screening_identifier="12345",
            report_datetime=get_utcnow() - relativedelta(days=1),
            age_in_years=25,
            eligible=True,
        )
        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()
        self.assertEqual(SubjectRefusal.objects.all().count(), 1)
