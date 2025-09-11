from datetime import timedelta
from unittest import skip

from clinicedc_tests.admin import TestModel5Admin
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.forms import TestModel5Form
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectConsentV1, TestModel5
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.test.client import RequestFactory

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.forms import AppointmentForm
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import NO
from edc_facility.import_holidays import import_holidays
from edc_form_label.custom_label_condition import CustomLabelCondition
from edc_form_label.form_label import FormLabel
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY01, MONTH2
from edc_visit_schedule.models import OnSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit


class TestFormLabel(TestCase):

    helper = Helper

    @classmethod
    def setUpTestData(cls):
        admin.site.register(TestModel5, TestModel5Admin)
        import_holidays()
        return super().setUpTestData()

    def setUp(self):

        self.user = User.objects.create(username="erikvw", is_staff=True, is_active=True)

        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        self.subject_identifier = subject_consent.subject_identifier

        for permission in Permission.objects.filter(
            content_type__app_label="clinicedc_tests", content_type__model="testmodel5"
        ):
            self.user.user_permissions.add(permission)
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

        SubjectConsentV1.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - timedelta(days=15),
        )

        OnSchedule.objects.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - timedelta(days=15),
        )
        self.appointment_one = Appointment.objects.get(visit_code=DAY01)

        self.subject_visit_one = SubjectVisit.objects.create(
            appointment=self.appointment_one,
            visit_code=self.appointment_one.visit_code,
            visit_code_sequence=self.appointment_one.visit_code_sequence,
            visit_schedule_name=self.appointment_one.visit_schedule_name,
            schedule_name=self.appointment_one.visit_schedule,
            reason=SCHEDULED,
        )
        self.appointment_one.appt_status = INCOMPLETE_APPT
        self.appointment_one.save()

        self.appointment_two = Appointment.objects.get(visit_code=MONTH2)

        self.subject_visit_two = SubjectVisit.objects.create(
            appointment=self.appointment_two,
            visit_code=self.appointment_two.visit_code,
            visit_code_sequence=self.appointment_two.visit_code_sequence,
            visit_schedule_name=self.appointment_two.visit_schedule_name,
            schedule_name=self.appointment_two.visit_schedule,
            reason=SCHEDULED,
        )
        for field in TestModel5._meta.get_fields():
            if field.name == "circumcised":
                self.default_label = field.verbose_name
                break

    def test_init(self):
        form_label = FormLabel(
            field="circumcised",
            custom_label="New label",
            condition_cls=CustomLabelCondition,
        )

        rf = RequestFactory()
        request = rf.get(f"/?appointment={str(self.appointment_one.id)}")
        request.user = self.user

        form = AppointmentForm()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=TestModel5, form=form),
            self.default_label,
        )

    def test_basics(self):
        class MyCustomLabelCondition(CustomLabelCondition):
            def check(self):
                if self.appointment.visit_code == MONTH2:
                    return True
                return False

        form_label = FormLabel(
            field="circumcised",
            custom_label="My custom label",
            condition_cls=MyCustomLabelCondition,
        )

        rf = RequestFactory()
        request = rf.get(f"/?appointment={str(self.appointment_one.id)}")
        request.user = self.user

        form = TestModel5Form()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=TestModel5, form=form),
            self.default_label,
        )

        rf = RequestFactory()
        request = rf.get(f"/?appointment={str(self.appointment_two.id)}")
        request.user = self.user

        form = TestModel5Form()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=TestModel5, form=form),
            form_label.custom_label,
        )

    def test_custom_label_as_template(self):
        class MyCustomLabelCondition(CustomLabelCondition):
            def check(self):
                return True if self.appointment.visit_code == MONTH2 else False

        form_label = FormLabel(
            field="circumcised",
            custom_label=(
                "The appointment is {appointment}. "
                "The previous appointment is {previous_appointment}. "
                "The previous obj is {previous_obj}. "
                "The previous visit is {previous_visit}."
            ),
            condition_cls=MyCustomLabelCondition,
        )

        rf = RequestFactory()
        request = rf.get(f"/?appointment={str(self.appointment_two.id)}")
        request.user = self.user

        form = TestModel5Form()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=TestModel5, form=form),
            "The appointment is 2000.0. "
            "The previous appointment is 1000.0. "
            "The previous obj is None. "
            "The previous visit is 1234 1000.0.",
        )

    @skip
    def test_custom_form_labels_default(self):
        for model, model_admin in admin.site._registry.items():
            if model == TestModel5:
                my_model_admin = model_admin.admin_site._registry.get(TestModel5)
                rf = RequestFactory()
                request = rf.get(f"/?appointment={str(self.appointment_one.id)}")
                request.user = self.user
                rendered_change_form = my_model_admin.changeform_view(
                    request, None, "", {"subject_visit": self.subject_visit_one}
                )
                self.assertIn("Are you circumcised", rendered_change_form.rendered_content)

    @skip
    def test_custom_form_labels_2(self):
        TestModel5.objects.create(subject_visit=self.subject_visit_one, circumcised=NO)

        for model, model_admin in admin.site._registry.items():
            if model == TestModel5:
                my_model_admin = model_admin.admin_site._registry.get(TestModel5)
                rf = RequestFactory()
                request = rf.get(f"/?appointment={str(self.appointment_two.id)}")
                request.user = self.user

                rendered_change_form = my_model_admin.changeform_view(
                    request, None, "", {"subject_visit": self.subject_visit_two}
                )
                self.assertNotIn("Are you circumcised", rendered_change_form.rendered_content)
                self.assertIn(
                    "Since we last saw you in ", rendered_change_form.rendered_content
                )
