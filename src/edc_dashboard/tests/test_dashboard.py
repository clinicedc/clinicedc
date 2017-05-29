from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.views.generic.base import TemplateView

from edc_base_test.mixins.dates_test_mixin import DatesTestMixin
from edc_dashboard.view_mixins.dashboard.appointment_mixin import AppointmentMixin
from edc_dashboard.view_mixins.dashboard.next_url_mixin import NextUrlMixin
from edc_dashboard.view_mixins.dashboard.consent_mixin import ConsentMixin
from edc_example.test_mixins import TestMixin
from edc_example.models import SubjectConsent
from edc_base_test.utils import get_utcnow


class TestDashboard(DatesTestMixin, TestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.make_enrolled_subject()
        self.assertIsNotNone(self.appointments)
        self.add_visit(self.appointments[0])
        self.request = RequestFactory().get('/')
        self.request.user = 'erik'

    def test_appointments(self):
        self.assertIsNotNone(self.subject_consent)
        self.assertIsNotNone(self.enrollment)
        self.assertIsNotNone(self.appointments)

    def test_next_url(self):
        view = NextUrlMixin()
        view.kwargs = {}
        self.assertEqual(view.get_next_url(), '')

    def test_next_url_add_paramters_no_values(self):
        """Assert if values not in kwargs parameters are removed."""
        class Dummy(NextUrlMixin, TemplateView):
            @property
            def next_url_parameters(self):
                parameters = super().next_url_parameters
                parameters.update({
                    'appointment': ['subject_identifier', 'selected_obj'],
                    'visit': ['subject_identifier', 'appointment']})
                return parameters
        view = Dummy()
        view.kwargs = {}
        options = {}
        self.assertEqual(view.get_next_url(**options), '')

    def test_next_url_add_paramters_with_values(self):
        """Assert if values in kwargs parameters are not removed."""
        class Dummy(NextUrlMixin, TemplateView):
            @property
            def next_url_parameters(self):
                parameters = super().next_url_parameters
                parameters.update({
                    'appointment': ['subject_identifier', 'selected_obj'],
                    'visit': ['subject_identifier', 'appointment']})
                return parameters
        view = Dummy()
        view.kwargs = {'subject_identifier': '123456-0'}
        self.assertEqual(
            view.get_next_url('appointment'),
            'dashboard_url,subject_identifier&subject_identifier=123456-0')

    def test_next_url_add_paramters_with_values_ignores_others(self):
        class Dummy(NextUrlMixin, TemplateView):
            @property
            def next_url_parameters(self):
                parameters = super().next_url_parameters
                parameters.update({
                    'appointment': ['subject_identifier', 'selected_obj'],
                    'visit': ['subject_identifier', 'appointment']})
                return parameters
        view = Dummy()
        view.kwargs = {'subject_identifier': '123456-0'}
        options = {'some_value': 'abcdef'}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier=123456-0')

    def test_appointment_next_url_no_values(self):
        class Dummy(AppointmentMixin, TemplateView):
            pass
        view = Dummy()
        view.kwargs = {}
        self.assertEqual(
            view.get_next_url('appointment'), '')

    def test_appointment_next_url_values(self):
        class Dummy(AppointmentMixin, TemplateView):
            pass
        view = Dummy()
        view.kwargs = {'subject_identifier': self.subject_identifier}
        options = {}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier={}'.format(self.subject_identifier))

    def test_appointment_next_url_gets_values_from_reponse(self):
        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        view = Dummy()
        # attrs from url
        view.kwargs = {'subject_identifier': self.subject_identifier}
        options = {}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier={}'.format(self.subject_identifier))

    def test_appointment_next_url_gets_values_from_reponse_ignores_unwanted(self):
        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        view = Dummy()
        view.kwargs = {
            'subject_identifier': self.subject_identifier,
            'unwanted_thing': 'unwanted_value'}  # attrs from url
        options = {}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier={}'.format(self.subject_identifier))

    def test_appointment_next_url_gets_values_from_reponse2(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

            @property
            def next_url_parameters(self):
                parameters = super().next_url_parameters
                parameters['appointment'].append('wanted_thing')
                return parameters

        view = Dummy()
        view.kwargs = {
            'subject_identifier': self.subject_identifier,
            'wanted_thing': 'wanted_value'}  # attrs from url
        options = {}
        next_url = view.get_next_url('appointment', **options)
        # should appear in querystring twice
        self.assertEqual(len(next_url.split('wanted_thing')), 3)
        self.assertIn('wanted_thing=wanted_value', next_url)

    def test_sets_subject_identifier(self):
        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'
        kwargs = {
            'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(response.context_data.get(
            'subject_identifier'), self.subject_identifier)

    def test_sets_appointment(self):
        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'
        appointment = self.appointments[0]
        kwargs = {
            'subject_identifier': self.subject_identifier,
            'appointment': appointment.id}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(response.context_data.get('appointment'), appointment)

    def test_sets_appointments(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(
            len(response.context_data.get('appointments')), self.appointments.count())

    def test_appointment_wrapper(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        for appointment in response.context_data.get('appointments'):
            self.assertTrue(appointment.next_url)

    def test_appointment_has_visit_next_url(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {
            'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        for appointment in response.context_data.get('appointments'):
            self.assertTrue(appointment.visit_next_url)

    def test_appointment_has_visit_next_url2(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        appointment = self.appointments[0]
        kwargs = {
            'subject_identifier': self.subject_identifier,
            'appointment': appointment.id}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertIsNotNone(
            response.context_data.get('appointment').visit_next_url)

    def test_appointment_has_visit_next_url3(self):

        class Dummy(AppointmentMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        appointment = self.appointments[0]
        kwargs = {
            'subject_identifier': self.subject_identifier,
            'appointment': appointment.id}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(
            response.context_data.get('appointment').visit_next_url,
            'dashboard_url,subject_identifier,appointment&subject_identifier={}&appointment={}'.format(
                self.subject_identifier, appointment.pk))

    @tag('me3')
    def test_consent(self):

        class Dummy(ConsentMixin, TemplateView):
            template_name = 'edc_dashboard.html'
            consent_model = SubjectConsent

            def get_utcnow(self):
                return get_utcnow()

        subject_consents = SubjectConsent.objects.filter(
            subject_identifier=self.subject_identifier)
        self.assertGreater(subject_consents.count(), 0)
        kwargs = {
            'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(
            len(response.context_data.get('consents')), subject_consents.count())
        self.assertEqual(
            response.context_data.get('consent'), self.subject_consent)
