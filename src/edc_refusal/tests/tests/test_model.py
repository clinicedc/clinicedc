from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_utils.date import get_utcnow

from edc_refusal.forms import SubjectRefusalForm
from edc_refusal.models import RefusalReasons, SubjectRefusal

from ...utils import get_subject_refusal_model, get_subject_refusal_model_cls
from ..models import SubjectScreening


class TestForms(TestCase):
    @staticmethod
    def get_data():
        refusal_reason = RefusalReasons.objects.all()[0]
        return {
            "screening_identifier": "12345",
            "report_datetime": get_utcnow(),
            "reason": refusal_reason,
            "other_reason": None,
            "comment": None,
        }

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_model_funcs(self):
        self.assertEqual(get_subject_refusal_model(), "edc_refusal.subjectrefusal")
        self.assertEqual(get_subject_refusal_model_cls(), SubjectRefusal)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_subject_refusal_ok(self):
        SubjectScreening.objects.create(
            screening_identifier="12345",
            report_datetime=get_utcnow() - relativedelta(days=1),
            age_in_years=25,
            eligible=True,
            refused=False,
        )
        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()
        self.assertEqual(SubjectRefusal.objects.all().count(), 1)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_add_subject_refusal_set_subject_screening_refused_true(self):
        subject_screening = SubjectScreening.objects.create(
            screening_identifier="12345",
            report_datetime=get_utcnow() - relativedelta(days=1),
            age_in_years=25,
            eligible=True,
            refused=False,
        )
        self.assertFalse(subject_screening.refused)

        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.save()
        subject_screening.refresh_from_db()
        self.assertTrue(subject_screening.refused)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_delete_subject_refusal_sets_subject_screening_refused_false(self):
        subject_screening = SubjectScreening.objects.create(
            screening_identifier="12345",
            report_datetime=get_utcnow() - relativedelta(days=1),
            age_in_years=25,
            eligible=True,
            refused=False,
        )
        self.assertFalse(subject_screening.refused)

        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.save()
        subject_screening.refresh_from_db()
        self.assertTrue(subject_screening.refused)

        subject_refusal = SubjectRefusal.objects.get(
            screening_identifier=subject_screening.screening_identifier
        )
        subject_refusal.delete()
        subject_screening.refresh_from_db()
        self.assertFalse(subject_screening.refused)
