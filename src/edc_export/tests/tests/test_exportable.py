import json
from tempfile import mkdtemp

from clinicedc_tests.sites import all_sites
from django.apps import apps as django_apps
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from edc_appointment.models import Appointment
from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths
from edc_export.auths import update_site_auths
from edc_export.constants import EXPORT
from edc_export.exportables import Exportables
from edc_export.model_options import ModelOptions
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("export1")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(),
    EDC_EXPORT_UPLOAD_FOLDER=mkdtemp(),
    SITE_ID=10,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
    EDC_AUTH_SKIP_SITE_AUTHS=False,
)
class TestExportable(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

        # rebuild site_auth and run authupdate
        site_auths.initialize()
        update_site_auths()
        AuthUpdater(verbose=False, warn_only=True)

    def setUp(self):
        group = Group.objects.get(name=EXPORT)
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
