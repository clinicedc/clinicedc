from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from edc_appointment.constants import MISSED_APPT
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import (
    ALIVE,
    COMPLETE,
    NO,
    NOT_APPLICABLE,
    ON_STUDY,
    PARTICIPANT,
    YES,
)
from edc_facility.import_holidays import import_holidays
from edc_metadata.constants import MISSED
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.exceptions import RelatedVisitReasonError
from edc_visit_tracking.form_validators import VisitFormValidator
from edc_visit_tracking.modelform_mixins import (
    VisitTrackingCrfModelFormMixin,
    VisitTrackingModelFormMixin,
)
from edc_visit_tracking.models import SubjectVisit
from visit_tracking_app.consents import consent_v1
from visit_tracking_app.models import BadCrfNoRelatedVisit, CrfOne
from visit_tracking_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


class SubjectVisitForm(VisitTrackingModelFormMixin, forms.ModelForm):
    form_validator_cls = VisitFormValidator

    class Meta:
        model = SubjectVisit
        fields = "__all__"


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestForm(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2022, 6, 11, 8, 00, tzinfo=utc_tz),
    )
    @time_machine.travel(datetime(2019, 7, 12, 8, 00, tzinfo=utc_tz))
    def test_visit_tracking_form_ok(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 6, 12, 8, 00, tzinfo=utc_tz),
        )

        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]

        data = dict(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            info_source=PARTICIPANT,
            study_status=ON_STUDY,
            survival_status=ALIVE,
            reason=SCHEDULED,
            reason_unscheduled=NOT_APPLICABLE,
            document_status=COMPLETE,
            require_crfs=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_visit_tracking_form__appt_not_missed_but_visit_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]

        data = dict(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            info_source=PARTICIPANT,
            study_status=ON_STUDY,
            survival_status=ALIVE,
            reason=MISSED,
            reason_unscheduled=NOT_APPLICABLE,
            document_status=COMPLETE,
            require_crfs=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitForm(data=data)
        form.is_valid()
        self.assertIn("reason", form._errors)

    def test_visit_tracking_form__appt_missed_but_visit_not_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 5, 11, 00, tzinfo=utc_tz),
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]

        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()

        data = dict(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            info_source=PARTICIPANT,
            study_status=ON_STUDY,
            survival_status=ALIVE,
            reason=SCHEDULED,
            reason_unscheduled=NOT_APPLICABLE,
            document_status=COMPLETE,
            require_crfs=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitForm(data=data)
        form.is_valid()
        self.assertIn("reason", form._errors)

    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2022, 6, 11, 8, 00, tzinfo=utc_tz),
    )
    @time_machine.travel(datetime(2019, 7, 12, 8, 00, tzinfo=utc_tz))
    def test_visit_tracking_form__missed_ok(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 6, 12, 8, 00, tzinfo=utc_tz),
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]

        SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]

        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]

        # note if appt_timing = MISSED_APPT, will auto create subject visit
        # see VisitModelManager
        subject_visit = SubjectVisit.objects.get(appointment=appointment)

        data = dict(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            info_source=PARTICIPANT,
            study_status=ON_STUDY,
            survival_status=ALIVE,
            reason=MISSED,
            reason_unscheduled=NOT_APPLICABLE,
            document_status=COMPLETE,
            require_crfs=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitForm(data=data, instance=subject_visit)
        form.is_valid()
        form.save(commit=True)
        obj = SubjectVisit.objects.get(appointment=appointment)
        self.assertEqual(NO, obj.require_crfs)

    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2022, 6, 11, 8, 00, tzinfo=utc_tz),
    )
    @time_machine.travel(datetime(2019, 7, 12, 8, 00, tzinfo=utc_tz))
    def test_visit_tracking_model__appt_missed_but_visit_not_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 6, 12, 00, tzinfo=utc_tz),
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]

        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()

        self.assertRaises(
            RelatedVisitReasonError,
            SubjectVisit.objects.create,
            appointment=appointment,
            reason=SCHEDULED,
        )

    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2022, 6, 11, 8, 00, tzinfo=utc_tz),
    )
    @time_machine.travel(datetime(2019, 7, 12, 8, 00, tzinfo=utc_tz))
    def test_crf_with_visit_tracking_form_ok(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 6, 12, 00, tzinfo=utc_tz),
        )
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": get_utcnow(),
                "subject_visit": subject_visit.pk,
                "site": Site.objects.get(id=settings.SITE_ID).id,
            }
        )

        self.assertTrue(form.is_valid())
        form.save(commit=True)

    def test_crf_with_visit_tracking_form_missing_subject_visit(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        appointment = Appointment.objects.all()[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": get_utcnow(),
                "site": Site.objects.get(id=settings.SITE_ID).id,
            }
        )
        form.is_valid()
        self.assertIn("subject_visit", form._errors)

    def test_crf_with_visit_tracking_form_missing_subject_visit_fk_raises(self):
        class BadCrfNoRelatedVisitorm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = BadCrfNoRelatedVisit
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        form = BadCrfNoRelatedVisitorm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": get_utcnow(),
                "site": Site.objects.get(id=settings.SITE_ID).id,
            }
        )
        self.assertRaises(ImproperlyConfigured, form.is_valid)

    def test_crf_with_visit_tracking_form_no_report_datetime(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "subject_visit": subject_visit.pk,
                "site": Site.objects.get(id=settings.SITE_ID).id,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("report_datetime", form._errors)

    def test_crf_with_visit_tracking_form_report_datetime_validated_against_related_visit(
        self,
    ):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
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
                    "site": Site.objects.get(id=settings.SITE_ID).id,
                }
            )
            self.assertFalse(form.is_valid())
            self.assertIn("report_datetime", form._errors)

    @override_settings(TIME_ZONE="Africa/Dar_es_Salaam")
    def test_crf_with_visit_tracking_form_report_datetime_zone(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
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
                    "site": Site.objects.get(id=settings.SITE_ID).id,
                }
            )
            self.assertFalse(form.is_valid())
            self.assertIn("report_datetime", form._errors)

    @override_settings(
        EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
        EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2022, 6, 11, 8, 00, tzinfo=utc_tz),
        TIME_ZONE="Africa/Dar_es_Salaam",
    )
    @time_machine.travel(datetime(2019, 7, 12, 8, 00, tzinfo=utc_tz))
    def test_crf_with_visit_tracking_form_report_datetime_zone2(self):
        class CrfForm(VisitTrackingCrfModelFormMixin, forms.ModelForm):
            report_datetime_field_attr = "report_datetime"

            class Meta:
                model = CrfOne
                fields = "__all__"

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=datetime(2019, 6, 12, 8, 00, tzinfo=utc_tz),
        )
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        form = CrfForm(
            {
                "f1": "1",
                "f2": "2",
                "f3": "3",
                "report_datetime": subject_visit.report_datetime,
                "subject_visit": subject_visit.pk,
                "site": Site.objects.get(id=settings.SITE_ID).id,
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
                "site": Site.objects.get(id=settings.SITE_ID).id,
            }
        )
        form.is_valid()
        self.assertIn("subject_visit", form._errors)
