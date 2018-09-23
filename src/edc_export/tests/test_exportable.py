import json

from django.apps import apps as django_apps
from django.contrib.auth.models import User, Group
from django.test import TestCase, tag
from django.test.client import RequestFactory
from edc_appointment.models.appointment import Appointment
from edc_registration.models import RegisteredSubject

from ..exportables import Exportables
from ..model_options import ModelOptions


class TestExportable(TestCase):

    def setUp(self):
        group = Group.objects.create(name='EXPORT')
        user = User.objects.create(
            username='erikvw', is_superuser=True, is_active=True)
        user.groups.add(group)
        self.request = RequestFactory()
        self.request.user = user
        self.user = user

    def test_model_options(self):

        model_opts = ModelOptions(model='edc_registration.registeredsubject')
        self.assertTrue(model_opts.label_lower)
        self.assertTrue(model_opts.verbose_name)
        self.assertFalse(model_opts.is_historical)
        self.assertFalse(model_opts.is_list_model)

        obj = json.dumps(model_opts)
        json.loads(obj)

    def test_model_options_historical(self):
        model_opts = ModelOptions(
            model='edc_appointment.historicalappointment')
        self.assertTrue(model_opts.label_lower)
        self.assertTrue(model_opts.verbose_name)
        self.assertTrue(model_opts.is_historical)
        self.assertFalse(model_opts.is_list_model)

        obj = json.dumps(model_opts)
        json.loads(obj)

    @tag('1')
    def test_exportables(self):
        registered_subject_opts = ModelOptions(
            model=RegisteredSubject._meta.label_lower)
        appointment_opts = ModelOptions(model=Appointment._meta.label_lower)
        edc_appointment = django_apps.get_app_config('edc_appointment')
        edc_registration = django_apps.get_app_config('edc_registration')
        exportables = Exportables(
            app_configs=[edc_registration, edc_appointment],
            request=self.request,
            user=self.user)
        self.assertIn(edc_registration, exportables.keys())
        self.assertIn(edc_appointment, exportables.keys())
        self.assertIn(
            registered_subject_opts.verbose_name,
            [o.verbose_name for o in exportables.get(
                edc_registration).get('models')])
        self.assertIn(
            appointment_opts.verbose_name,
            [o.verbose_name for o in exportables.get(
                edc_appointment).get('models')])
        self.assertFalse(exportables.get(edc_registration).get('historicals'))
        self.assertIn(
            'edc_appointment.historicalappointment',
            [o.label_lower for o in exportables.get(
                edc_appointment).get('historicals')])
        self.assertFalse(exportables.get(edc_registration).get('lists'))
        self.assertFalse(exportables.get(edc_appointment).get('lists'))
