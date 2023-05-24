import json
from tempfile import mkdtemp

from django.apps import apps as django_apps
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject

from edc_export.exportables import Exportables
from edc_export.model_options import ModelOptions


@override_settings(EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp())
class TestExportable(TestCase):
    def setUp(self):
        group = Group.objects.create(name="EXPORT")
        user = User.objects.create(username="erikvw", is_superuser=True, is_active=True)
        user.groups.add(group)
        self.request = RequestFactory()
        self.request.user = user
        self.user = user

    def test_model_options(self):
        model_opts = ModelOptions(model="edc_registration.registeredsubject")
        self.assertTrue(model_opts.label_lower)
        self.assertTrue(model_opts.verbose_name)
        self.assertFalse(model_opts.is_historical)
        self.assertFalse(model_opts.is_list_model)
        self.assertFalse(model_opts.is_inline)

        obj = json.dumps(model_opts)
        json.loads(obj)

    def test_model_options_historical(self):
        model_opts = ModelOptions(model="edc_appointment.historicalappointment")
        self.assertTrue(model_opts.label_lower)
        self.assertTrue(model_opts.verbose_name)
        self.assertTrue(model_opts.is_historical)
        self.assertFalse(model_opts.is_list_model)

        obj = json.dumps(model_opts)
        json.loads(obj)

    def test_exportables(self):
        registered_subject_opts = ModelOptions(model=RegisteredSubject._meta.label_lower)
        appointment_opts = ModelOptions(model=Appointment._meta.label_lower)
        edc_appointment = django_apps.get_app_config("edc_appointment")
        edc_registration = django_apps.get_app_config("edc_registration")
        exportables = Exportables(
            app_configs=[edc_registration, edc_appointment],
            request=self.request,
            user=self.user,
        )
        self.assertIn("edc_registration", exportables.keys())
        self.assertIn("edc_appointment", exportables.keys())

        self.assertIn(
            registered_subject_opts.verbose_name,
            [o.verbose_name for o in exportables.get("edc_registration").models],
        )
        self.assertIn(
            appointment_opts.verbose_name,
            [o.verbose_name for o in exportables.get("edc_appointment").models],
        )

        self.assertIn(
            "edc_registration.historicalregisteredsubject",
            [o.label_lower for o in exportables.get("edc_registration").historical_models],
        )
        self.assertIn(
            "edc_appointment.historicalappointment",
            [o.label_lower for o in exportables.get("edc_appointment").historical_models],
        )
        self.assertIn(
            "edc_appointment.appointmenttype",
            [o.label_lower for o in exportables.get("edc_appointment").list_models],
        )
        self.assertFalse(exportables.get("edc_registration").list_models)

    def test_default_exportables(self):
        exportables = Exportables(
            app_configs=None,
            request=self.request,
            user=self.user,
        )
        self.assertIn("django.contrib.admin", exportables)
        self.assertIn("django.contrib.auth", exportables)
        self.assertIn("django.contrib.sites", exportables)
