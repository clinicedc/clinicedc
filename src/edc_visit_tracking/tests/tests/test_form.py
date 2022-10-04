from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator
from edc_visit_tracking.modelform_mixins import VisitTrackingCrfModelFormMixin

from ..helper import Helper
from ..models import BadCrfNoRelatedVisit, CrfOne, SubjectVisit
from ..visit_schedule import visit_schedule1, visit_schedule2


class SubjectVisitForm(forms.ModelForm):
    form_validator_cls = VisitFormValidator

    class Meta:
        model = SubjectVisit
        fields = "__all__"


class TestForm(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )

    def test_visit_tracking_form_ok(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": get_utcnow(),
                "subject_visit": subject_visit.pk,
            }
        )
        self.assertTrue(form.is_valid())
        form.save(commit=True)

    def test_visit_tracking_form_missing_subject_visit(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm({"f1": "1", "f2": "2", "f3": "3", "report_datetime": get_utcnow()})
        form.is_valid()
        self.assertIn("subject_visit", form._errors)

    def test_visit_tracking_form_missing_subject_visit_fk_raises(self):
        class BadCrfNoRelatedVisitorm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = BadCrfNoRelatedVisit
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        form = BadCrfNoRelatedVisitorm(
            {"f1": "1", "f2": "2", "f3": "3", "report_datetime": get_utcnow()}
        )
        self.assertRaises(ImproperlyConfigured, form.is_valid)

    def test_visit_tracking_form_no_report_datetime(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm({"f1": "1", "f2": "2", "f3": "3", "subject_visit": subject_visit.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("report_datetime", form._errors)

    def test_visit_tracking_form_report_datetime_validated_against_related_visit(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        for report_datetime in [
            get_utcnow() - relativedelta(months=1),
            get_utcnow() + relativedelta(months=1),
        ]:
            form = CrfForm(
                {
                    "f1": "1",
                    "f2": "2",
                    "f3": "3",
                    "report_datetime": report_datetime,
                    "subject_visit": subject_visit.pk,
                }
            )
            self.assertFalse(form.is_valid())
            self.assertIn("report_datetime", form._errors)

    @override_settings(TIME_ZONE="Africa/Dar_es_Salaam")
    def test_visit_tracking_form_report_datetime_zone(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=get_utcnow(),
        )
        dte = get_utcnow().astimezone(ZoneInfo("Africa/Dar_es_Salaam"))
        for report_datetime in [
            dte - relativedelta(months=1),
            dte + relativedelta(months=1),
        ]:
            form = CrfForm(
                {
                    "f1": "1",
                    "f2": "2",
                    "f3": "3",
                    "report_datetime": report_datetime,
                    "subject_visit": subject_visit.pk,
                }
            )
            self.assertFalse(form.is_valid())
            self.assertIn("report_datetime", form._errors)

    @override_settings(TIME_ZONE="Africa/Dar_es_Salaam")
    def test_visit_tracking_form_report_datetime_zone2(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": subject_visit.report_datetime,
                "subject_visit": subject_visit.pk,
            }
        )
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save(commit=True)

        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": subject_visit.report_datetime,
                "subject_visit": subject_visit.pk,
            }
        )
        form.is_valid()
        self.assertIn("subject_visit", form._errors)
