from django import forms
from django.test import TestCase
from edc_constants.constants import DM, HIV, HTN, NO, NOT_APPLICABLE, YES
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import FormValidator
from model_bakery import baker

from dx_app.models import ClinicalReviewBaseline
from edc_dx import get_diagnosis_labels
from edc_dx.form_validators import DiagnosisFormValidatorMixin

from ..test_case_mixin import TestCaseMixin


class DiagnosisFormValidator(
    CrfFormValidatorMixin, DiagnosisFormValidatorMixin, FormValidator
):
    def clean(self):
        self.get_diagnoses()
        for prefix, label in get_diagnosis_labels():
            self.applicable_if_not_diagnosed(
                prefix=prefix,
                field_applicable=f"{prefix}_test",
                label=label,
            )

    def get_consent_for_period_or_raise(self):
        pass


class MyModel:
    @classmethod
    def related_visit_model_attr(cls):
        return "subject_visit"


class TestDiagnosisFormValidator(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = self.enroll()
        self.create_visits(self.subject_identifier)

    def test_ok(self):
        data = dict(subject_visit=self.subject_visit_followup)
        form_validator = DiagnosisFormValidator(cleaned_data=data, model=MyModel)
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn(
            f"Please complete {ClinicalReviewBaseline._meta.verbose_name}",
            str(form_validator._errors.get("__all__")),
        )

    def test_ok2(self):
        data = dict(subject_visit=self.subject_visit_followup)
        form_validator = DiagnosisFormValidator(cleaned_data=data, model=MyModel)
        self.assertRaises(forms.ValidationError, form_validator.validate)
        self.assertIn(
            f"Please complete {ClinicalReviewBaseline._meta.verbose_name}",
            str(form_validator._errors.get("__all__")),
        )


class ApplicableIfDiagnosedFormValidator(
    DiagnosisFormValidatorMixin, CrfFormValidatorMixin, FormValidator
):
    def clean(self):
        for prefix, label in get_diagnosis_labels().items():
            self.applicable_if_diagnosed(
                diagnoses=self.get_diagnoses(),
                prefix=prefix,
                field_applicable=f"{prefix}_test",
                label=label,
            )


class TestApplicableIfDiagnosedFormValidation(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_identifier = self.enroll()
        self.create_visits(self.subject_identifier)

    def test_no_dx_ok(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=NO,
            dm_dx=NO,
            htn_dx=NO,
        )
        cleaned_data = {
            "subject_visit": self.subject_visit_baseline,
            "hiv_test": NOT_APPLICABLE,
            "dm_test": NOT_APPLICABLE,
            "htn_test": NOT_APPLICABLE,
        }
        form_validator = ApplicableIfDiagnosedFormValidator(
            cleaned_data=cleaned_data, model=MyModel
        )
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_no_dx_with_answer_raises(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=NO,
            dm_dx=NO,
            htn_dx=NO,
        )

        for cond in [HIV.lower(), DM, HTN]:
            for answer in [YES, NO]:
                with self.subTest(cond=cond, answer=answer):
                    cleaned_data = {
                        "subject_visit": self.subject_visit_baseline,
                        "hiv_test": NOT_APPLICABLE,
                        "dm_test": NOT_APPLICABLE,
                        "htn_test": NOT_APPLICABLE,
                    }

                    cleaned_data.update({f"{cond}_test": answer})

                    form_validator = ApplicableIfDiagnosedFormValidator(
                        cleaned_data=cleaned_data, model=MyModel
                    )
                    with self.assertRaises(forms.ValidationError) as cm:
                        form_validator.validate()
                    self.assertIn(f"{cond}_test", cm.exception.error_dict)
                    self.assertIn(
                        "Patient was not previously diagnosed with "
                        f"{get_diagnosis_labels().get(cond)}.",
                        str(cm.exception.error_dict.get(f"{cond}_test")),
                    )

    def test_hiv_dx_yes_requires_answer(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
            dm_dx=NO,
            htn_dx=NO,
        )
        baker.make(
            "dx_app.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )
        cleaned_data = {
            "subject_visit": self.subject_visit_baseline,
            "hiv_test": NOT_APPLICABLE,
            "dm_test": NOT_APPLICABLE,
            "htn_test": NOT_APPLICABLE,
        }
        form_validator = ApplicableIfDiagnosedFormValidator(
            cleaned_data=cleaned_data, model=MyModel
        )
        with self.assertRaises(forms.ValidationError) as cm:
            form_validator.validate()
        self.assertIn("hiv_test", cm.exception.error_dict)
        self.assertIn(
            "Patient was previously diagnosed with HIV. Expected YES or NO.",
            str(cm.exception.error_dict.get("hiv_test")),
        )

        for answer in [YES, NO]:
            with self.subTest(answer=answer):
                cleaned_data.update({"hiv_test": answer})
                form_validator = ApplicableIfDiagnosedFormValidator(
                    cleaned_data=cleaned_data, model=MyModel
                )
                try:
                    form_validator.validate()
                except forms.ValidationError as e:
                    self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_all_dx_yes_requires_answer(self):
        baker.make(
            "dx_app.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_dx=YES,
            dm_dx=YES,
            htn_dx=YES,
        )
        baker.make(
            "dx_app.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            rx_init_ago="4y",
        )
        baker.make(
            "dx_app.dminitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="2y",
            rx_init_ago="1y",
        )
        baker.make(
            "dx_app.htninitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="1y",
            rx_init_ago="1y",
        )

        cleaned_data = {
            "subject_visit": self.subject_visit_baseline,
            "hiv_test": YES,
            "dm_test": YES,
            "htn_test": YES,
        }
        form_validator = ApplicableIfDiagnosedFormValidator(
            cleaned_data=cleaned_data, model=MyModel
        )
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        for cond in [HIV.lower(), DM, HTN]:
            with self.subTest(cond=cond):
                cleaned_data = {
                    "subject_visit": self.subject_visit_baseline,
                    "hiv_test": YES,
                    "dm_test": YES,
                    "htn_test": YES,
                }
                cleaned_data.update({f"{cond}_test": NOT_APPLICABLE})
                form_validator = ApplicableIfDiagnosedFormValidator(
                    cleaned_data=cleaned_data, model=MyModel
                )
                with self.assertRaises(forms.ValidationError) as cm:
                    form_validator.validate()
                self.assertIn(f"{cond}_test", cm.exception.error_dict)
                self.assertIn(
                    f"Patient was previously diagnosed with "
                    f"{get_diagnosis_labels().get(cond)}. Expected YES or NO.",
                    str(cm.exception.error_dict.get(f"{cond}_test")),
                )
