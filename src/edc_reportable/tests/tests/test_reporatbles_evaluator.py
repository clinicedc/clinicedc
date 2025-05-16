# from dateutil.relativedelta import relativedelta
# from django.core.exceptions import ValidationError
# from django.db.models import Count
# from django.test import TestCase, tag
# from edc_constants.constants import FEMALE, MALE, NO, NOT_APPLICABLE, YES
# from edc_utils import get_utcnow
#
# from edc_reportable import (
#     GRADE0,
#     GRADE1,
#     GRADE2,
#     GRADE3,
#     GRADE4,
#     GRADE5,
#     GRAMS_PER_DECILITER,
#     IU_LITER,
#     MICROMOLES_PER_LITER,
#     MILLIGRAMS_PER_DECILITER,
#     MILLIMOLES_PER_LITER,
#     TEN_X_9_PER_LITER,
# )
# from edc_reportable.evaluator import ValueBoundryError
# from edc_reportable.exceptions import NotEvaluated
# from edc_reportable.models import (
#     GradingData,
#     NormalData,
#     get_normal_data_or_raise,
#     in_bounds_or_raise,
# )
# from edc_reportable.models.load_data import load_reference_ranges
# from edc_reportable.models.utils.get_grading_data_or_raise import (
#     get_grading_data_or_raise,
# )
# from edc_reportable.reportables_evaluator import ReportablesEvaluator
# from edc_reportable.value_reference_group import BoundariesOverlap
# from reportable_app.reportables import grading_data, normal_data
#
#
# class TestLoadData(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         load_reference_ranges(
#             "my_reportables", grading_data=grading_data, normal_data=normal_data
#         )
#
#     def setUp(self):
#         self.assertEqual(NormalData.objects.all().count(), 20)
#         self.assertEqual(GradingData.objects.all().count(), 60)
#         self.cleaned_data = {
#             "subject_visit": "",
#             "dob": get_utcnow() - relativedelta(years=25),
#             "gender": FEMALE,
#             "haemoglobin": 15,
#             "haemoglobin_units": GRAMS_PER_DECILITER,
#             "haemoglobin_abnormal": NO,
#             "haemoglobin_reportable": NOT_APPLICABLE,
#             "alt": 10,
#             "alt_units": IU_LITER,
#             "alt_abnormal": NO,
#             "alt_reportable": NOT_APPLICABLE,
#             "magnesium": 0.8,
#             "magnesium_units": MILLIMOLES_PER_LITER,
#             "magnesium_abnormal": NO,
#             "magnesium_reportable": NOT_APPLICABLE,
#             "creatinine": 100,
#             "creatinine_units": MICROMOLES_PER_LITER,
#             "creatinine_abnormal": NO,
#             "creatinine_reportable": NOT_APPLICABLE,
#             "neutrophil": 3,
#             "neutrophil_units": TEN_X_9_PER_LITER,
#             "neutrophil_abnormal": NO,
#             "neutrophil_reportable": NOT_APPLICABLE,
#             "sodium": 135,
#             "sodium_units": MILLIMOLES_PER_LITER,
#             "sodium_abnormal": NO,
#             "sodium_reportable": NOT_APPLICABLE,
#             "potassium": 4.0,
#             "potassium_units": MILLIMOLES_PER_LITER,
#             "potassium_abnormal": NO,
#             "potassium_reportable": NOT_APPLICABLE,
#             "platelets": 450,
#             "platelets_units": TEN_X_9_PER_LITER,
#             "platelets_abnormal": NO,
#             "platelets_reportable": NOT_APPLICABLE,
#             "results_normal": YES,
#             "results_reportable": NOT_APPLICABLE,
#         }
#
#     @tag("7")
#     def test_reportables_evaluator(self):
#
#         grades: list[str] = [GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5]
#
#         def get_value_relative_to_limit_normal(self, value: str) -> int | float:
#             """Return either upper or lower boundary value as a literal
#             value or as a value relative to the lower limit normal or
#             upper limit normal.
#
#             Parameter `value` may be a float, None or a string
#
#             If LLN or ULN, uses normal reference value.
#             """
#             pattern = rf"(\d+\.\d+)\*({LLN}|{ULN})"
#             try:
#                 value = value.upper()
#             except AttributeError:
#                 pass
#             else:
#                 if not re.match(pattern, value):
#                     raise GradeReferenceError(
#                         f"Invalid value. Unable to parse value string for {LLN} or {ULN}. "
#                         f"Got {value}."
#                     )
#                 else:
#                     factor, limit_normal_label = value.split("*")
#                     if limit_normal_label == LLN:
#                         value = float(factor) * self.normal_reference.lower
#                     elif limit_normal_label == ULN:
#                         value = float(factor) * self.normal_reference.upper
#             return value
#
#         def get_grade_or_raise(value, **kwargs):
#             else:
#             raise BoundariesOverlap(
#                 f"Previously got {grade}. "
#                 f"Got {grade_ref.description(value=value)} ",
#                 "Check your definitions.",
#             )
#
#
#         class Result:
#             def __init__(self, value, description):
#                 self._value = value
#                 self.description = description(value=value)
#
#             def __str__(self):
#                 return self.description
#
#         class Grade(Result):
#             def __init__(self, value, grade, description):
#                 super().__init__(value, description)
#                 self.grade = grade
#
#         def get_grade_or_raise(value=None, **kwargs):
#             """Returns a Grade instance or None."""
#             grade = None
#             for grading_data in get_grading_data_or_raise(**kwargs):
#                 grade = in_bounds_or_raise(value=value, **kwargs):
#                 grade = Grade(value, grade_ref.grade, grade_ref.description)
#                     else:
#                         raise BoundariesOverlap(
#                             f"Previously got {grade}. "
#                             f"Got {grade_ref.description(value=value)} ",
#                             "Check your definitions.",
#                         )
#             return grade
#
#         for field, value in self.cleaned_data.items():
#             try:
#                 utest_id, _ = field.split("_value")
#             except ValueError:
#                 utest_id = field
#                 if value is not None and GradingData.objects.filter(label=utest_id).exists():
#                     self._evaluate_reportable(utest_id, value, field)
