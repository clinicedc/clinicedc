from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.test import TestCase, tag
from django.test.client import RequestFactory
from edc_appointment.models import Appointment
from edc_utils import get_utcnow
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .admin import VISIT_ONE, VISIT_TWO
from .models import MyModel, SubjectVisit, MyModel2
from .visit_schedule import visit_schedule


class TestFieldsetAdmin(TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.user = User.objects.create(
            username="erikvw", is_staff=True, is_active=True
        )
        self.subject_identifier = "1234"
        for permission in Permission.objects.filter(
            content_type__app_label="edc_fieldsets"
        ):
            self.user.user_permissions.add(permission)
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_fieldset_excluded(self):
        """Asserts the conditional fieldset is not added
        to the model admin instance for this appointment.

        VISIT_ONE
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code=VISIT_ONE,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        subject_visit = SubjectVisit.objects.create(appointment=appointment)

        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)
        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")

        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertIn("form-row field-f1", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f2", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f3", rendered_change_form.rendered_content)
        self.assertNotIn("form-row field-f4", rendered_change_form.rendered_content)
        self.assertNotIn("form-row field-f5", rendered_change_form.rendered_content)

    def test_fieldset_included(self):
        """Asserts the conditional fieldset IS added
        to the model admin instance for this appointment.

        VISIT_TWO
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow() - timedelta(days=1),
            timepoint=0,
            visit_code=VISIT_ONE,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        SubjectVisit.objects.create(appointment=appointment)
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code=VISIT_TWO,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )

        subject_visit = SubjectVisit.objects.create(appointment=appointment)

        for model, model_admin in admin.site._registry.items():
            if model == MyModel:
                my_model_admin = model_admin.admin_site._registry.get(MyModel)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")
        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertIn("form-row field-f1", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f2", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f3", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f4", rendered_change_form.rendered_content)
        self.assertIn("form-row field-f5", rendered_change_form.rendered_content)

    def test_fieldset_moved_to_end(self):
        """Asserts the conditional fieldset IS inserted
        but `Summary` and `Audit` fieldsets remain at the end.

        VISIT_TWO
        """
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow() - timedelta(days=1),
            timepoint=0,
            visit_code=VISIT_ONE,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        SubjectVisit.objects.create(appointment=appointment)
        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code=VISIT_TWO,
            visit_code_sequence=0,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        subject_visit = SubjectVisit.objects.create(appointment=appointment)

        for model, model_admin in admin.site._registry.items():
            if model == MyModel2:
                my_model_admin = model_admin.admin_site._registry.get(MyModel2)

        rf = RequestFactory()

        request = rf.get(f"/?appointment={str(appointment.id)}")
        request.user = self.user

        rendered_change_form = my_model_admin.changeform_view(
            request, None, "", {"subject_visit": subject_visit}
        )

        self.assertLess(
            rendered_change_form.rendered_content.find("id_f4"),
            rendered_change_form.rendered_content.find("id_summary_one"),
        )
