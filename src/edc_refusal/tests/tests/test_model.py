from django.test import TestCase, tag
from edc_utils.date import get_utcnow


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

    def test_screening_ok(self):

        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()
        self.assertEqual(SubjectRefusal.objects.all().count(), 1)
