from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import FEMALE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow

from edc_reportable import (
    GRAMS_PER_DECILITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIMOLES_PER_LITER,
    TEN_X_9_PER_LITER,
    site_reportables,
)
from edc_reportable.units import MILLIGRAMS_PER_DECILITER
from reportable_app.form_validators import SpecimenResultFormValidator
from reportable_app.models import SpecimenResult
from reportable_app.reportables import grading_data, normal_data


class TestSpecimenResultForm(TestCase):
    def setUp(self):
        site_reportables._registry = {}

        site_reportables.register(
            name="my_reference_list", normal_data=normal_data, grading_data=grading_data
        )

        self.cleaned_data = {
            "subject_visit": "",
            "dob": get_utcnow() - relativedelta(years=25),
            "gender": FEMALE,
            "haemoglobin": 15,
            "haemoglobin_units": GRAMS_PER_DECILITER,
            "haemoglobin_abnormal": NO,
            "haemoglobin_reportable": NOT_APPLICABLE,
            "alt": 10,
            "alt_units": IU_LITER,
            "alt_abnormal": NO,
            "alt_reportable": NOT_APPLICABLE,
            "magnesium": 0.8,
            "magnesium_units": MILLIMOLES_PER_LITER,
            "magnesium_abnormal": NO,
            "magnesium_reportable": NOT_APPLICABLE,
            "creatinine": 100,
            "creatinine_units": MICROMOLES_PER_LITER,
            "creatinine_abnormal": NO,
            "creatinine_reportable": NOT_APPLICABLE,
            "neutrophil": 3,
            "neutrophil_units": TEN_X_9_PER_LITER,
            "neutrophil_abnormal": NO,
            "neutrophil_reportable": NOT_APPLICABLE,
            "sodium": 135,
            "sodium_units": MILLIMOLES_PER_LITER,
            "sodium_abnormal": NO,
            "sodium_reportable": NOT_APPLICABLE,
            "potassium": 4.0,
            "potassium_units": MILLIMOLES_PER_LITER,
            "potassium_abnormal": NO,
            "potassium_reportable": NOT_APPLICABLE,
            "platelets": 450,
            "platelets_units": TEN_X_9_PER_LITER,
            "platelets_abnormal": NO,
            "platelets_reportable": NOT_APPLICABLE,
            "results_normal": YES,
            "results_reportable": NOT_APPLICABLE,
        }

    def test_haemoglobin_units_invalid(self):
        self.cleaned_data.update(haemoglobin=6.4, results_abnormal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("haemoglobin", form_validator._errors)

    def test_haemoglobin_units_male_valid(self):
        self.cleaned_data.update(haemoglobin=14, results_abnormal=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got{e}")

    def test_no_creatinine_mg_invalid(self):
        self.cleaned_data.update(creatinine=0.3, creatinine_units=MILLIGRAMS_PER_DECILITER)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("creatinine", form_validator._errors)

    def test_no_creatinine_mg_sodium_invalid(self):
        self.cleaned_data.update(
            creatinine=900, creatinine_units=MICROMOLES_PER_LITER, results_abnormal=YES
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("creatinine", form_validator._errors)

    def test_creatinine_mg_invalid(self):
        self.cleaned_data.update(
            creatinine=2.48,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            results_abnormal=YES,
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("creatinine", form_validator._errors)

    def test_creatinine_mg(self):
        self.cleaned_data.update(
            creatinine=1.3,
            creatinine_units=MILLIGRAMS_PER_DECILITER,
            results_abnormal=NO,
            results_reportable=NOT_APPLICABLE,
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_creatinine_umol_invalid(self):
        self.cleaned_data.update(
            creatinine=217,
            creatinine_units=MICROMOLES_PER_LITER,
            are_results_normal=YES,
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("creatinine", form_validator._errors)

    def test_creatinine_umol(self):
        self.cleaned_data.update(creatinine=100, creatinine_units=MICROMOLES_PER_LITER)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got{e}")

    def test_magnesium_invalid(self):
        self.cleaned_data.update(magnesium=0.01, are_results_normal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("magnesium", form_validator._errors)

    def test_magnesium(self):
        self.cleaned_data.update(magnesium=0.35, results_abnormal=YES, results_reportable=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("magnesium", form_validator._errors)

    def test_potassium_invalid(self):
        self.cleaned_data.update(potassium=1.0, results_abnormal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("potassium", form_validator._errors)

    def test_potassium_high(self):
        self.cleaned_data.update(potassium=6.8, results_abnormal=YES, results_reportable=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("potassium", form_validator._errors)

    def test_potassium_low(self):
        self.cleaned_data.update(potassium=2.3, results_abnormal=YES, results_reportable=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("potassium", form_validator._errors)

    def test_sodium_invalid(self):
        self.cleaned_data.update(sodium=100, results_abnormal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("sodium", form_validator._errors)

    def test_sodium_invalid_1(self):
        self.cleaned_data.update(
            sodium=119, results_abnormal=YES, results_reportable=NOT_APPLICABLE
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("sodium", form_validator._errors)

    def test_sodium_invalid_2(self):
        self.cleaned_data.update(sodium=119, results_abnormal=YES, results_reportable=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("sodium", form_validator._errors)

    def test_sodium(self):
        self.cleaned_data.update(
            sodium=135, results_abnormal=NO, results_reportable=NOT_APPLICABLE
        )
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got{e}")

    def test_alt_invalid(self):
        self.cleaned_data.update(alt=201, are_results_normal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("alt", form_validator._errors)

    def test_alt(self):
        self.cleaned_data.update(alt=10, results_abnormal=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got{e}")

    def test_platelets_invalid(self):
        self.cleaned_data.update(platelets=50, results_abnormal=YES)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("platelets", form_validator._errors)

    def test_platelets(self):
        self.cleaned_data.update(platelets=450, results_abnormal=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_neutrophil_invalid(self):
        self.cleaned_data.update(neutrophil=0.5)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("neutrophil", form_validator._errors)

    def test_neutrophil(self):
        self.cleaned_data.update(neutrophil=4, results_abnormal=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got{e}")

    def test_results_reportable_invalid(self):
        self.cleaned_data.update(sodium=1000, results_abnormal=YES, results_reportable=NO)
        form_validator = SpecimenResultFormValidator(
            cleaned_data=self.cleaned_data, instance=SpecimenResult()
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("sodium", form_validator._errors)
