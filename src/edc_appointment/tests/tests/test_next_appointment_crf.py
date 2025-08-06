import calendar
import datetime as dt
from decimal import Decimal
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase, override_settings, tag
from edc_consent.site_consents import site_consents
from edc_constants.constants import CLINIC, NO, PATIENT
from edc_facility import import_holidays
from edc_facility.models import HealthFacility, HealthFacilityTypes
from edc_facility.utils import get_health_facility_model_cls
from edc_metadata.metadata_handler import MetadataHandlerError
from edc_sites.utils import get_site_model_cls
from edc_utils import get_utcnow
from edc_visit_schedule.models import VisitSchedule
from edc_visit_schedule.post_migrate_signals import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_appointment.exceptions import AppointmentWindowError
from edc_appointment.models import Appointment, InfoSources
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.forms import (
    NextAppointmentCrfForm,
    NextAppointmentCrfFormValidator,
)
from edc_appointment_app.models import NextAppointmentCrf, SubjectConsent
from edc_appointment_app.visit_schedule import get_visit_schedule6

utc = ZoneInfo("UTC")
tz = ZoneInfo("Africa/Dar_es_Salaam")


def update_health_facility_model():
    from edc_sites.site import sites as site_sites

    try:
        clinic = HealthFacilityTypes.objects.get(name=CLINIC)
    except ObjectDoesNotExist:
        clinic = HealthFacilityTypes.objects.create(name=CLINIC, display_name=CLINIC)
    for site_obj in get_site_model_cls().objects.all():
        single_site = site_sites.get(site_obj.id)
        get_health_facility_model_cls().objects.create(
            name=single_site.name,
            title=single_site.title,
            health_facility_type=clinic,
            mon=True,
            tue=True,
            wed=True,
            thu=True,
            fri=True,
            sat=False,
            sun=False,
            site_id=site_obj.id,
        )


@override_settings(SITE_ID=10)
class TestNextAppointmentCrf(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        update_health_facility_model()
        # health_facility_type = HealthFacilityTypes.objects.create(
        #     name="clinic", display_name="clinic"
        # )
        # HealthFacility.objects.create(
        #     name="clinic",
        #     health_facility_type=health_facility_type,
        #     mon=True,
        #     tue=True,
        #     wed=True,
        #     thu=True,
        #     fri=True,
        #     sat=False,
        #     sun=False,
        # )
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule6())
        site_consents.registry = {}
        site_consents.register(consent_v1)
        populate_visit_schedule()

        self.subject_identifier = "101-40990029-4"
        identity = "123456789"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_appointment_app.onschedulesix"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def test_next_appt_ok(self):
        health_facility_type = HealthFacilityTypes.objects.create(
            name="Integrated", display_name="Integrated"
        )
        health_facility = HealthFacility.objects.create(
            name="integrated_facility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=True,
            wed=False,
            thu=True,
            fri=False,
            sat=False,
            sun=False,
        )
        self.assertEqual(5, Appointment.objects.all().count())

        # update appt/visit 1000
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit = get_related_visit_model_cls().objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )
        # from 1000, attempt to update NextAppointmentCrf
        # incorrectly link this to visit code 1000, the current
        data = dict(
            subject_visit=subject_visit.id,
            site=subject_visit.site,
            report_datetime=subject_visit.report_datetime,
            appt_date=appointment.next.appt_datetime.date(),
            visitschedule=VisitSchedule.objects.get(visit_code="1000"),
            info_source=InfoSources.objects.get(name=PATIENT),
            health_facility=health_facility.id,
            offschedule_today=NO,
        )
        obj = NextAppointmentCrf(subject_visit=subject_visit, health_facility=health_facility)
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()

        self.assertIn("visitschedule", form._errors)
        self.assertIn("Cannot be the current visit", str(form._errors.get("visitschedule")))

        # still from 1000, attempt to update NextAppointmentCrf
        # but this time correctly link this to visit code 1010
        self.assertEqual(
            calendar.MONDAY,
            calendar.weekday(
                data.get("appt_date").year,
                data.get("appt_date").month,
                data.get("appt_date").day,
            ),
        )
        data.update(visitschedule=VisitSchedule.objects.get(visit_code="1010"))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("Invalid clinic day", str(form._errors.get("appt_date")))

        data.update(appt_date=appointment.next.appt_datetime.date() + relativedelta(days=1))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        del form._errors["subject_visit"]
        self.assertEqual({}, form._errors)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        }
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc))
    def test_next_appt_with_health_facility(self):
        self.assertEqual(get_utcnow().weekday(), 1)  # tues
        health_facility_type = HealthFacilityTypes.objects.create(
            name="Integrated", display_name="Integrated"
        )
        health_facility = HealthFacility.objects.create(
            name="integrated_facility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=True,
            wed=False,
            thu=True,
            fri=False,
            sat=False,
            sun=False,
        )
        self.assertEqual(5, Appointment.objects.all().count())
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls = get_related_visit_model_cls()
        subject_visit = subject_visit_model_cls.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )

        data = dict(
            report_datetime=subject_visit.report_datetime,
            appt_date=(
                appointment.appt_datetime + relativedelta(months=3) + relativedelta(days=3)
            ).date(),
            info_source=InfoSources.objects.get(name=PATIENT),
            visitschedule=VisitSchedule.objects.get(visit_code="1030"),
            health_facility=health_facility.id,
        )
        self.assertEqual(data.get("appt_date").weekday(), 4)
        obj = NextAppointmentCrf(subject_visit=subject_visit)
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("appt_date", form._errors)
        self.assertIn("Invalid clinic day", str(form._errors.get("appt_date")))

        data.update(appt_date=data.get("appt_date") + relativedelta(days=1))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertIn("appt_date", form._errors)
        self.assertIn("Expected Mon-Fri", str(form._errors.get("appt_date")))

        data.update(appt_date=data.get("appt_date") - relativedelta(days=2))
        form = NextAppointmentCrfForm(data=data, instance=obj)
        form.is_valid()
        self.assertNotIn("appt_date", form._errors)

    @override_settings(
        EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING={
            "edc_appointment_app.nextappointmentcrf": ("appt_date", "visitschedule")
        },
        LANGUAGE_CODE="sw",
    )
    @time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=tz))
    def test_next_appt_with_health_facility_tz(self):
        self.assertEqual(get_utcnow().weekday(), 1)  # tues
        health_facility_type = HealthFacilityTypes.objects.create(
            name="Integrated", display_name="Integrated"
        )
        health_facility = HealthFacility.objects.create(
            name="integrated_facility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=True,
            wed=False,
            thu=True,
            fri=False,
            sat=False,
            sun=False,
        )
        appointment = Appointment.objects.get(timepoint=0)
        subject_visit_model_cls = get_related_visit_model_cls()
        subject_visit = subject_visit_model_cls.objects.create(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.report_datetime,
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=(
                appointment.appt_datetime + relativedelta(months=3) + relativedelta(days=2)
            ).date(),
            info_source=InfoSources.objects.get(name=PATIENT),
            visitschedule=VisitSchedule.objects.get(visit_code="1030"),
            health_facility=health_facility.id,
        )
        self.assertEqual(data.get("appt_date").weekday(), 3)

    @tag("1")
    def test_in_visit_crfs(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
            )
        try:
            NextAppointmentCrf.objects.create(
                subject_visit=subject_visit,
                report_datetime=subject_visit.report_datetime,
                appt_date=subject_visit.appointment.next.appt_datetime.date(),
                health_facility=HealthFacility.objects.all()[0],
                visitschedule=VisitSchedule.objects.get(
                    visit_schedule_name=subject_visit.visit_schedule.name,
                    schedule_name=subject_visit.schedule.name,
                    timepoint=subject_visit.appointment.next.timepoint,
                ),
            )
        except MetadataHandlerError as e:
            self.fail(f"Unexpected MetadataHandlerError. Got {e}")

    def test_nextappt_updates_the_next_appointment_appt_datetime(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
            )
        next_appt = subject_visit.appointment.next
        original_next_appt_datetime = next_appt.appt_datetime
        obj = NextAppointmentCrf(
            appt_date=original_next_appt_datetime.date() + relativedelta(days=1),
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=next_appt.timepoint,
            ),
        )
        obj.save()
        next_appt = Appointment.objects.get(timepoint=next_appt.timepoint)
        self.assertEqual(
            next_appt.appt_datetime.date(),
            original_next_appt_datetime.date() + relativedelta(days=1),
        )

    def test_next_appt_date_same_as_original_next_appt(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
            )
        next_appt = subject_visit.appointment.next
        next_appt_date = next_appt.appt_datetime.date()
        NextAppointmentCrf.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=next_appt_date,
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=next_appt.timepoint,
            ),
        )
        next_appt.refresh_from_db()
        self.assertEqual(next_appt_date, next_appt.appt_datetime.date())

    def test_updates_next_appointment_datetime(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
            )
        next_appt = subject_visit.appointment.next
        next_appt_date = subject_visit.appointment.next.appt_datetime.date() + relativedelta(
            days=1
        )
        NextAppointmentCrf.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=next_appt_date,
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=next_appt.visit_schedule.name,
                timepoint=next_appt.timepoint,
            ),
        )
        next_appt.refresh_from_db()
        self.assertEqual(next_appt.appt_datetime.date(), next_appt_date)

    def test_raises_if_next_appointment_datetime_is_before_current(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )
        next_appt = subject_visit.appointment.next
        current_appt_datetime = subject_visit.appointment.appt_datetime
        self.assertRaises(
            ValidationError,
            NextAppointmentCrf.objects.create,
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=current_appt_datetime.date(),
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=next_appt.timepoint,
            ),
        )

        with self.assertRaises(ValidationError) as cm:
            NextAppointmentCrf.objects.create(
                subject_visit=subject_visit,
                report_datetime=subject_visit.report_datetime,
                appt_date=current_appt_datetime.date(),
                health_facility=HealthFacility.objects.all()[0],
                visitschedule=VisitSchedule.objects.get(
                    visit_schedule_name=subject_visit.visit_schedule.name,
                    timepoint=next_appt.timepoint,
                ),
            )
        self.assertIn("Cannot be equal to the report datetime", str(cm.exception))

    def test_raises_on_appt_date_outside_of_window_for_selected_visit_code(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )
        next_appt = subject_visit.appointment.next
        bad_next_date = subject_visit.report_datetime.date() + relativedelta(days=1)
        self.assertRaises(
            AppointmentWindowError,
            NextAppointmentCrf.objects.create,
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=bad_next_date,
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=next_appt.timepoint,
            ),
        )

    def test_next_appt_form_validator_ok(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        # get to 1010
        for timepoint in [0, 1]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )

        defaults = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            health_facility=HealthFacility.objects.get(site=subject_visit.site),
        )

        # use next visit code
        visitschedule = VisitSchedule.objects.get(
            visit_schedule_name=subject_visit.visit_schedule.name,
            timepoint=subject_visit.appointment.next.timepoint,
        )

        # set appt date to that of the next appointment, visit_code to
        # next visit code
        cleaned_data = dict(
            appt_date=subject_visit.appointment.next.appt_datetime.date(),
            visitschedule=visitschedule,
            **defaults,
        )

        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_next_appt_form_validator_not_on_weekend(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        # get to 1010
        for timepoint in [0, 1]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )

        defaults = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            health_facility=HealthFacility.objects.get(site=subject_visit.site),
        )

        # use next visit code
        visitschedule = VisitSchedule.objects.get(
            visit_schedule_name=subject_visit.visit_schedule.name,
            timepoint=subject_visit.appointment.next.timepoint,
        )

        # find a weekend date
        appt_date = subject_visit.appointment.next.appt_datetime.date()
        for i in range(0, 7):
            appt_date = appt_date + relativedelta(days=1)
            if appt_date.weekday() in (calendar.SATURDAY, calendar.SUNDAY):
                break

        # set appt date to that of the next appointment, visit_code to
        # next visit code
        cleaned_data = dict(appt_date=appt_date, visitschedule=visitschedule, **defaults)

        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("Expected Mon-Fri", str(cm.exception))

    def test_next_appt_form_validator_cannot_be_current_visit_code(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )
        cleaned_data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=subject_visit.report_datetime.date() + relativedelta(days=1),
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=subject_visit.appointment.timepoint,
            ),
        )
        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("Cannot be the current visit", str(cm.exception))

    def test_next_appt_form_validator_appt_date_must_be_in_next_window(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit = subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )
        cleaned_data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            appt_date=subject_visit.report_datetime.date() + relativedelta(days=1),
            health_facility=HealthFacility.objects.all()[0],
            visitschedule=VisitSchedule.objects.get(
                visit_schedule_name=subject_visit.visit_schedule.name,
                timepoint=subject_visit.appointment.next.timepoint,
            ),
        )

        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("Date falls outside of the window period", str(cm.exception))

        cleaned_data.update(
            appt_date=subject_visit.report_datetime.date() + relativedelta(years=1)
        )
        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("Date falls outside of the window period", str(cm.exception))

    def test_next_appt_form_validator_next_apptdate_cannot_be_changed_if_not_new(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )

        # go back to 1010
        subject_visit = subject_visit_model_cls.objects.get(
            appointment__timepoint=Decimal("1.0")
        )

        defaults = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            health_facility=HealthFacility.objects.all()[0],
        )

        # use next visit code
        visitschedule = VisitSchedule.objects.get(
            visit_schedule_name=subject_visit.visit_schedule.name,
            timepoint=subject_visit.appointment.next.timepoint,
        )

        # set appt date to that of the next appointment, visit_code to
        # next visit code
        cleaned_data = dict(
            appt_date=subject_visit.appointment.next.appt_datetime.date()
            + relativedelta(days=1),
            visitschedule=visitschedule,
            **defaults,
        )

        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("Next appointment has already started", str(cm.exception))

    @tag("1")
    def test_next_appt_form_validator_next_ok_if_appt_date_not_changed(self):
        subject_visit_model_cls = get_related_visit_model_cls()
        for timepoint in [0, 1, 2]:
            appointment = Appointment.objects.get(timepoint=timepoint)
            subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=SCHEDULED,
                report_datetime=appointment.report_datetime,
                site=appointment.site,
            )

        # go back to 1010
        subject_visit = subject_visit_model_cls.objects.get(
            appointment__timepoint=Decimal("1.0")
        )

        defaults = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            health_facility=HealthFacility.objects.get(site=subject_visit.site),
        )

        # use next visit code
        visitschedule = VisitSchedule.objects.get(
            visit_schedule_name=subject_visit.visit_schedule.name,
            timepoint=subject_visit.appointment.next.timepoint,
        )

        # set appt date to that of the next appointment, visit_code to
        # next visit code
        cleaned_data = dict(
            appt_date=subject_visit.appointment.next.appt_datetime.date(),
            visitschedule=visitschedule,
            **defaults,
        )

        form_validator = NextAppointmentCrfFormValidator(
            cleaned_data=cleaned_data, model=NextAppointmentCrf
        )
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly. Got {e}")
