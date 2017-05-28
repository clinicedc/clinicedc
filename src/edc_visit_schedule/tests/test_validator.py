from django.test import TestCase, tag

from ..models_validator import Validator, ValidatorLookupError, ValidatorMetaValueError
from ..models_validator import ValidatorModelFieldError, ValidatorMetaAttributeError, ValidatorMetaFormatError
from .models import Enrollment, Disenrollment, SubjectVisit


@tag('validator')
class TestValidator(TestCase):

    def test_validator_init(self):
        """Asserts determines name from visit schedule and schedule names.
        """
        validator = Validator(visit_schedule_name='visit_schedule_name')
        self.assertEqual(validator.name, 'visit_schedule_name')
        validator = Validator(schedule_name='schedule_name')
        self.assertEqual(validator.name, 'schedule_name')

    def test_validator_init2(self):
        """Asserts chooses visit_schedule_name over and schedule_name.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule_name', schedule_name='schedule_name')
        self.assertEqual(validator.name, 'visit_schedule_name')

    def test_repr(self):
        validator = Validator(
            visit_schedule_name='visit_schedule_name', schedule_name='schedule_name')
        self.assertIsNotNone(repr(validator))

    def test_str(self):
        validator = Validator(
            visit_schedule_name='visit_schedule_name', schedule_name='schedule_name')
        self.assertIsNotNone(str(validator))

    def test_get_model_cls(self):
        validator = Validator(
            visit_schedule_name='visit_schedule_name', model='edc_visit_schedule.enrollment')
        self.assertEqual(Enrollment, validator._model)

    def test_get_model_cls_raises(self):
        validator = Validator(
            visit_schedule_name='visit_schedule_name', model='blah')
        try:
            validator._model
        except ValidatorLookupError:
            pass
        else:
            self.fail('ValidatorError unexpectedly not raised.')

    def test_get_model_cls_raises2(self):
        validator = Validator(
            visit_schedule_name='visit_schedule_name', model='blah.blah')
        try:
            validator._model
        except ValidatorLookupError:
            pass
        else:
            self.fail('ValidatorError unexpectedly not raised.')

    def test_validated_model_raises(self):
        """Asserts raises if no model provided.
        """
        validator = Validator()
        try:
            validator.validated_model
        except ValidatorLookupError:
            pass
        else:
            self.fail('ValidatorError unexpectedly not raised.')

    def test_validated_model_raises1(self):
        """Asserts raises if bad model (label_lower).
        """
        validator = Validator(
            visit_schedule_name='visit_schedule_name', model='blah.blah')
        try:
            validator.validated_model
        except ValidatorLookupError:
            pass
        else:
            self.fail('ValidatorError unexpectedly not raised.')

    def test_validated_model1(self):
        """Asserts returns expected model class.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule', model='edc_visit_schedule.enrollment')
        self.assertEqual(validator.validated_model, Enrollment)

    def test_validated_model2(self):
        """Asserts returns expected model class.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule', model='edc_visit_schedule.disenrollment')
        self.assertEqual(validator.validated_model, Disenrollment)

    def test_validated_model_raises_missing_meta(self):
        """Asserts raises if model class is missing meta attr.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule', model='edc_visit_schedule.subjectvisit')
        try:
            validator.validated_model
        except ValidatorMetaAttributeError:
            pass
        else:
            self.fail('ValidatorMetaAttributeError unexpectedly not raised.')

    def test_validated_model_without_requiring_meta(self):
        """Asserts does not raise if model class is missing meta attr
        when no visit schedule/schedule specified.
        """
        validator = Validator(model='edc_visit_schedule.subjectvisit')
        self.assertEqual(validator.validated_model, SubjectVisit)

    def test_validates_model_with_required_fields(self):
        """Asserts returns expected model class.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule',
            model='edc_visit_schedule.disenrollment',
            required_fields=['report_datetime'])
        self.assertEqual(validator.validated_model, Disenrollment)

    def test_raises_if_missing_required_fields(self):
        """Asserts returns expected model class.
        """
        validator = Validator(
            visit_schedule_name='visit_schedule',
            model='edc_visit_schedule.disenrollment',
            required_fields=['blah'])
        try:
            validator.validated_model
        except ValidatorModelFieldError:
            pass
        else:
            self.fail('ValidatorModelFieldError unexpectedly not raised.')

    def test_validated_model_raises_invalid_model_meta(self):
        """Asserts raises .
        """
        validator = Validator(
            schedule_name='schedule', model='edc_visit_schedule.badmetamodel')
        try:
            validator.validated_model
        except ValidatorMetaValueError:
            pass
        else:
            self.fail('ValidatorMetaValueError unexpectedly not raised.')

    def test_validated_model_raises_invalid_model_meta_pattern(self):
        """Asserts raises .
        """
        validator = Validator(
            schedule_name='schedule', model='edc_visit_schedule.enrollment',
            meta_pattern=r'^[A-Z]+$')
        try:
            validator.validated_model
        except ValidatorMetaFormatError:
            pass
        else:
            self.fail('ValidatorMetaFormatError unexpectedly not raised.')
