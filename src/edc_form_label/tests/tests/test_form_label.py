from datetime import timedelta
from unittest import skip

from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.test.client import RequestFactory
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_constants.constants import NO
from edc_facility import import_holidays
from edc_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ...custom_label_condition import CustomLabelCondition
from ...form_label import FormLabel
from ..admin import VISIT_ONE, VISIT_TWO
from ..forms import MyForm
from ..models import MyModel, OnSchedule, SubjectVisit
from ..visit_schedule import visit_schedule


class TestFormLabel(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        return super().setUpTestData()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        self.user = User.objects.create(username="erikvw", is_staff=True, is_active=True)
        self.subject_identifier = "1234"
        for permission in Permission.objects.filter(
            content_type__app_label="edc_form_label", content_type__model="mymodel"
        ):
            self.user.user_permissions.add(permission)
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow() - timedelta(days=15),
            onschedule_datetime=get_utcnow() - timedelta(days=15),
        )
        self.appointment_one = Appointment.objects.get(visit_code=VISIT_ONE)

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

        self.appointment_two = Appointment.objects.get(visit_code=VISIT_TWO)

        self.subject_visit_two = SubjectVisit.objects.create(
            appointment=self.appointment_two,
            visit_code=self.appointment_two.visit_code,
            visit_code_sequence=self.appointment_two.visit_code_sequence,
            visit_schedule_name=self.appointment_two.visit_schedule_name,
            schedule_name=self.appointment_two.visit_schedule,
            reason=SCHEDULED,
        )
        for field in MyModel._meta.get_fields():
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

        form = MyForm()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=MyModel, form=form),
            self.default_label,
        )

    def test_basics(self):
        class MyCustomLabelCondition(CustomLabelCondition):
            def check(self):
                if self.appointment.visit_code == VISIT_TWO:
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

        form = MyForm()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=MyModel, form=form),
            self.default_label,
        )

        rf = RequestFactory()
        request = rf.get(f"/?appointment={str(self.appointment_two.id)}")
        request.user = self.user

        form = MyForm()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=MyModel, form=form),
            form_label.custom_label,
        )

    def test_custom_label_as_template(self):
        class MyCustomLabelCondition(CustomLabelCondition):
            def check(self):
                return True if self.appointment.visit_code == VISIT_TWO else False

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

        form = MyForm()

        self.assertEqual(
            form_label.get_form_label(request=request, obj=None, model=MyModel, form=form),
            "The appointment is 2000.0. "
            "The previous appointment is 1000.0. "
            "The previous obj is None. "
            "The previous visit is 1234 1000.0.",
        )

    def test_custom_form_labels_default(self):
        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)
                rf = RequestFactory()
                request = rf.get(f"/?appointment={str(self.appointment_one.id)}")
                request.user = self.user
                rendered_change_form = my_model_admin.changeform_view(
                    request, None, "", {"subject_visit": self.subject_visit_one}
                )
                self.assertIn("Are you circumcised", rendered_change_form.rendered_content)

    @skip
    def test_custom_form_labels_2(self):
        MyModel.objects.create(subject_visit=self.subject_visit_one, circumcised=NO)

        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)
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
