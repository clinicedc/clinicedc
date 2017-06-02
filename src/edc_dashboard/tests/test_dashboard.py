from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.views.generic.base import TemplateView

# from edc_base_test.mixins.dates_test_mixin import DatesTestMixin
from edc_consent.tests.models import SubjectConsent
from edc_visit_schedule.tests.models import Enrollment, Disenrollment, SubjectVisit
# from edc_model_wrapper.url_mixins import NextUrlMixin
# from edc_example.test_mixins import TestMixin
# from edc_example.models import SubjectConsent
from edc_base.utils import get_utcnow
from edc_appointment.models import Appointment

from ..view_mixins import AppointmentViewMixin, ConsentViewMixin
from django.apps import apps as django_apps

from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents
from edc_constants.constants import MALE, FEMALE
from edc_visit_schedule.visit_schedule.visit_schedule import VisitSchedule
from edc_visit_schedule.schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

app_config = django_apps.get_app_config('edc_protocol')

subjectconsent_v1 = Consent(
    'edc_consent.subjectconsent',
    version='1',
    start=app_config.study_open_datetime,
    end=app_config.study_close_datetime,
    age_min=16,
    age_is_adult=18,
    age_max=64,
    gender=[MALE, FEMALE],
    subject_type='subject')

site_consents.register(subjectconsent_v1)

visit_schedule = VisitSchedule(
    name='visit_schedule',
    verbose_name='Visit Schedule',
    visit_model=SubjectVisit)
#     offstudy_model=SubjectOffstudy,
#     death_report_model=DeathReport,
#     enrollment_model=Enrollment,
#     disenrollment_model=Disenrollment)

schedule = Schedule(
    name='schedule',
    enrollment_model=Enrollment._meta.label_lower,
    disenrollment_model=Disenrollment)
visit_schedule.add_schedule(schedule)
site_visit_schedules.register(visit_schedule)


# class TestDashboard(DatesTestMixin, TestMixin, TestCase):
class TestDashboard(TestCase):

    def add_visit(self, appointment):
        SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED)

    def make_enrolled_subject(self):
        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier='11111111',
            consent_datetime=get_utcnow(),
            identity='111111111',
            confirm_identity='111111111')
        self.enrollment = Enrollment.objects.create(
            subject_identifier='11111111',
            report_datetime=self.subject_consent.consent_datetime)
        self.appointments = Appointment.objects.all().order_by('appt_datetime')
        self.subject_identifier = self.subject_consent.subject_identifier

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

    def test_appointment_next_url_no_values(self):
        class Dummy(AppointmentViewMixin, TemplateView):
            pass
        view = Dummy()
        view.kwargs = {}
        self.assertEqual(
            view.get_next_url('appointment'), '')

    def test_appointment_next_url_values(self):
        class Dummy(AppointmentViewMixin, TemplateView):
            pass
        view = Dummy()
        view.kwargs = {'subject_identifier': self.subject_identifier}
        options = {}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier={}'.format(self.subject_identifier))

    def test_appointment_next_url_gets_values_from_reponse(self):
        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        view = Dummy()
        # attrs from url
        view.kwargs = {'subject_identifier': self.subject_identifier}
        options = {}
        self.assertEqual(
            view.get_next_url('appointment', **options),
            'dashboard_url,subject_identifier&subject_identifier={}'.format(self.subject_identifier))

    def test_appointment_next_url_gets_values_from_reponse_ignores_unwanted(self):
        class Dummy(AppointmentViewMixin, TemplateView):
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

        class Dummy(AppointmentViewMixin, TemplateView):
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
        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'
        kwargs = {
            'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(response.context_data.get(
            'subject_identifier'), self.subject_identifier)

    def test_sets_appointment(self):
        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'
        appointment = self.appointments[0]
        kwargs = {
            'subject_identifier': self.subject_identifier,
            'appointment': appointment.id}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(response.context_data.get('appointment'), appointment)

    def test_sets_appointments(self):

        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertEqual(
            len(response.context_data.get('appointments')), self.appointments.count())

    def test_appointment_wrapper(self):

        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        for appointment in response.context_data.get('appointments'):
            self.assertTrue(appointment.next_url)

    def test_appointment_has_visit_next_url(self):

        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        kwargs = {
            'subject_identifier': self.subject_identifier}
        response = Dummy.as_view()(self.request, **kwargs)
        for appointment in response.context_data.get('appointments'):
            self.assertTrue(appointment.visit_next_url)

    def test_appointment_has_visit_next_url2(self):

        class Dummy(AppointmentViewMixin, TemplateView):
            template_name = 'edc_dashboard.html'

        appointment = self.appointments[0]
        kwargs = {
            'subject_identifier': self.subject_identifier,
            'appointment': appointment.id}
        response = Dummy.as_view()(self.request, **kwargs)
        self.assertIsNotNone(
            response.context_data.get('appointment').visit_next_url)

    def test_appointment_has_visit_next_url3(self):

        class Dummy(AppointmentViewMixin, TemplateView):
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

        class Dummy(ConsentViewMixin, TemplateView):
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
