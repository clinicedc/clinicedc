from __future__ import print_function

from collections import OrderedDict

from django.test import TestCase
from django.utils import timezone

from edc_lab.lab_profile.classes import site_lab_profiles
from edc_lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc_testing.classes import TestLabProfile, TestAppConfiguration
from edc_testing.models import TestVisit, TestAliquotType, TestPanel

from edc_appointment.models import Appointment
from edc_base.utils import edc_base_startup
from edc_consent.models.consent_type import ConsentType
from edc_constants.constants import MALE, REQUIRED, NOT_ADDITIONAL, YES
from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_visit_schedule.classes import (
    VisitScheduleConfiguration, CrfTuple, RequisitionPanelTuple, MembershipFormTuple, ScheduleTuple)
from edc_visit_schedule.models import VisitDefinition


from .test_models import TestVisitModel, TestConsentModel

entries = (
    CrfTuple(10L, u'edc_testing', u'TestScheduledModel1', REQUIRED, NOT_ADDITIONAL),
    CrfTuple(20L, u'edc_testing', u'TestScheduledModel2', REQUIRED, NOT_ADDITIONAL),
    CrfTuple(30L, u'edc_testing', u'TestScheduledModel3', REQUIRED, NOT_ADDITIONAL),
)

requisitions = (
    RequisitionPanelTuple(
        10L, u'edc_testing', u'testrequisition', 'Research Blood Draw', 'TEST', 'WB', REQUIRED, NOT_ADDITIONAL),
    RequisitionPanelTuple(
        20L, u'edc_testing', u'testrequisition', 'Viral Load', 'TEST', 'WB', REQUIRED, NOT_ADDITIONAL),
    RequisitionPanelTuple(
        30L, u'edc_testing', u'testrequisition', 'Microtube', 'STORAGE', 'WB', REQUIRED, NOT_ADDITIONAL),
)


class VisitSchedule(VisitScheduleConfiguration):
    """A visit schedule class for tests."""
    name = 'Test Visit Schedule'
    app_label = 'edc_testing'
    panel_model = TestPanel
    aliquot_type_model = TestAliquotType

    membership_forms = OrderedDict({
        'schedule-1': MembershipFormTuple('schedule-1', TestConsentModel, True),
    })

    schedules = OrderedDict({
        'schedule-1': ScheduleTuple('schedule-1', 'schedule-1', None, None),
    })

    visit_definitions = OrderedDict(
        {'1000': {
            'title': '1000',
            'time_point': 0,
            'base_interval': 0,
            'base_interval_unit': 'D',
            'window_lower_bound': 0,
            'window_lower_bound_unit': 'D',
            'window_upper_bound': 0,
            'window_upper_bound_unit': 'D',
            'grouping': 'group1',
            'visit_tracking_model': TestVisitModel,
            'schedule': 'schedule-1',
            'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         '2000': {
             'title': '2000',
             'time_point': 1,
             'base_interval': 0,
             'base_interval_unit': 'D',
             'window_lower_bound': 0,
             'window_lower_bound_unit': 'D',
             'window_upper_bound': 0,
             'window_upper_bound_unit': 'D',
             'grouping': 'group1',
             'visit_tracking_model': TestVisitModel,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         '2000A': {
             'title': '2000A',
             'time_point': 0,
             'base_interval': 0,
             'base_interval_unit': 'D',
             'window_lower_bound': 0,
             'window_lower_bound_unit': 'D',
             'window_upper_bound': 0,
             'window_upper_bound_unit': 'D',
             'grouping': 'group2',
             'visit_tracking_model': TestVisit,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         '2010A': {
             'title': '2010A',
             'time_point': 1,
             'base_interval': 0,
             'base_interval_unit': 'D',
             'window_lower_bound': 0,
             'window_lower_bound_unit': 'D',
             'window_upper_bound': 0,
             'window_upper_bound_unit': 'D',
             'grouping': 'group2',
             'visit_tracking_model': TestVisit,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         '2020A': {
             'title': '2020A',
             'time_point': 2,
             'base_interval': 0,
             'base_interval_unit': 'D',
             'window_lower_bound': 0,
             'window_lower_bound_unit': 'D',
             'window_upper_bound': 0,
             'window_upper_bound_unit': 'D',
             'grouping': 'group2',
             'visit_tracking_model': TestVisit,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         '2030A': {
             'title': '2030A',
             'time_point': 3,
             'base_interval': 0,
             'base_interval_unit': 'D',
             'window_lower_bound': 0,
             'window_lower_bound_unit': 'D',
             'window_upper_bound': 0,
             'window_upper_bound_unit': 'D',
             'grouping': 'group2',
             'visit_tracking_model': TestVisit,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         },
    )


class BaseTestCase(TestCase):

    app_label = 'edc_testing'
    consent_catalogue_name = 'v1'

    def setUp(self):
        edc_base_startup()
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        TestAppConfiguration().prepare()
        # update consent type for our consent model
        consent_type = ConsentType.objects.first()
        consent_type.app_label = 'edc_offstudy'
        consent_type.model_name = 'testconsentmodel'
        consent_type.save()
        VisitSchedule().build()
        self.study_site = '40'
        self.identity = '111111111'
        self.subject_identifier = '999-100000-1'
        self.visit_definition = VisitDefinition.objects.get(code='1000')
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier=self.subject_identifier)
        self.test_consent = TestConsentModel.objects.create(
            registered_subject=self.registered_subject,
            consent_datetime=timezone.now(),
            is_literate=YES,
            gender=MALE,
            identity=self.identity,
            confirm_identity=self.identity,
            subject_identifier=self.subject_identifier)
        self.appointment_count = VisitDefinition.objects.all().count()
        self.appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=self.visit_definition)
