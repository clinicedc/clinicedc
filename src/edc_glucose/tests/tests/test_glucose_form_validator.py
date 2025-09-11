from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper as BaseHelper
from edc_consent import site_consents
from edc_constants.constants import NOT_APPLICABLE, YES
from edc_lab.constants import EQ
from edc_reportable import MILLIMOLES_PER_LITER
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_glucose.form_validators import GlucoseFormValidator

from ..consents import consent_v1
from ..models import SubjectScreening
from ..visit_schedules import visit_schedule


class Helper(BaseHelper):
    @property
    def screening_model_cls(self):
        return SubjectScreening


@override_settings(SITE_ID=10)
class TestGlucose(TestCase):
    helper_cls = Helper

    def setUp(self):
        SubjectScreening.objects.create(
            screening_identifier="ABCD",
            screening_datetime=get_utcnow(),
            subject_identifier="12345",
        )
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
        )
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )

        appointment_baseline = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]

        self.subject_visit_baseline = SubjectVisit.objects.create(
            appointment=appointment_baseline,
            subject_identifier=self.subject_identifier,
            visit_code=1000,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            reason=SCHEDULED,
        )
        appointment_followup = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[1]
        self.subject_visit_followup = SubjectVisit.objects.create(
            appointment=appointment_followup,
            subject_identifier=self.subject_identifier,
            visit_code="2000",
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            reason=SCHEDULED,
        )

    def test_glucose_result(self):
        class MyGlucoseFormValidator(GlucoseFormValidator):
            def clean(self):
                self.validate_glucose_test()

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=NOT_APPLICABLE,
            glucose_units=NOT_APPLICABLE,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_fasting", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_units=NOT_APPLICABLE,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_fasting_duration_str", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_fasting_duration_str="12h",
            glucose_units=NOT_APPLICABLE,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_date", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_fasting_duration_str="12h",
            glucose_date=get_utcnow().date,
            glucose_units=NOT_APPLICABLE,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_value", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_fasting_duration_str="12h",
            glucose_date=get_utcnow().date,
            glucose_value=5.3,
            glucose_units=MILLIMOLES_PER_LITER,
            glucose_quantifier=None,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_quantifier", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_fasting_duration_str="12h",
            glucose_date=get_utcnow().date,
            glucose_value=5.3,
            glucose_units=NOT_APPLICABLE,
            glucose_quantifier=EQ,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("glucose_units", cm.exception.error_dict)

        cleaned_data = dict(
            subject_visit=self.subject_visit_baseline,
            glucose_performed=YES,
            glucose_fasting=YES,
            glucose_fasting_duration_str="12h",
            glucose_date=get_utcnow().date,
            glucose_value=5.3,
            glucose_units=MILLIMOLES_PER_LITER,
            glucose_quantifier=EQ,
        )
        form_validator = MyGlucoseFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")
