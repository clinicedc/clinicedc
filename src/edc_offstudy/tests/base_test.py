from __future__ import print_function

from collections import OrderedDict

from django.db import models
from django.test import TestCase

from edc.core.bhp_variables.models import StudySite
from edc.entry_meta_data.models import MetaDataMixin
from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc.testing.classes import TestLabProfile, TestAppConfiguration
from edc.testing.models import TestVisit, TestConsentWithMixin, TestAliquotType, TestPanel
from edc.testing.tests.factories import TestConsentWithMixinFactory, TestVisitFactory
from edc_appointment.models import Appointment
from edc_constants.constants import MALE, REQUIRED, NOT_ADDITIONAL
from edc_offstudy.models import OffStudyMixin
from edc_visit_schedule.classes import (
    VisitScheduleConfiguration, EntryTuple, RequisitionPanelTuple, MembershipFormTuple, ScheduleGroupTuple)
from edc_visit_schedule.models import VisitDefinition
from edc_visit_tracking.models import BaseVisitTracking, PreviousVisitMixin, CrfModelMixin
from edc_offstudy.models.off_study_model_mixin import OffStudyModelMixin
from edc_base.model.models.base_uuid_model import BaseUuidModel


class TestVisitModel(OffStudyMixin, MetaDataMixin, PreviousVisitMixin, BaseVisitTracking):

    off_study_model = ('edc_offstudy', 'TestOffStudyModel')
    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'


class TestOffStudyModel(CrfModelMixin, OffStudyModelMixin, BaseUuidModel):

    test_visit_model = models.OneToOneField(TestVisitModel)

    class Meta:
        app_label = 'edc_offstudy'


class AnotherTestVisitModel(OffStudyMixin, MetaDataMixin, PreviousVisitMixin, BaseVisitTracking):

    off_study_model = TestOffStudyModel
    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'

entries = (
    EntryTuple(10L, u'testing', u'TestScheduledModel1', REQUIRED, NOT_ADDITIONAL),
    EntryTuple(20L, u'testing', u'TestScheduledModel2', REQUIRED, NOT_ADDITIONAL),
    EntryTuple(30L, u'testing', u'TestScheduledModel3', REQUIRED, NOT_ADDITIONAL),
)

requisitions = (
    RequisitionPanelTuple(
        10L, u'testing', u'testrequisition', 'Research Blood Draw', 'TEST', 'WB', REQUIRED, NOT_ADDITIONAL),
    RequisitionPanelTuple(
        20L, u'testing', u'testrequisition', 'Viral Load', 'TEST', 'WB', REQUIRED, NOT_ADDITIONAL),
    RequisitionPanelTuple(
        30L, u'testing', u'testrequisition', 'Microtube', 'STORAGE', 'WB', REQUIRED, NOT_ADDITIONAL),
)


class VisitSchedule(VisitScheduleConfiguration):
    """A visit schedule class for tests."""
    name = 'Test Visit Schedule'
    app_label = 'testing'
    panel_model = TestPanel
    aliquot_type_model = TestAliquotType

    membership_forms = OrderedDict({
        'schedule-1': MembershipFormTuple('schedule-1', TestConsentWithMixin, True),
    })

    schedule_groups = OrderedDict({
        'schedule-group-1': ScheduleGroupTuple('schedule-group-1', 'schedule-1', None, None),
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
            'schedule_group': 'schedule-group-1',
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
             'schedule_group': 'schedule-group-1',
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
             'schedule_group': 'schedule-group-1',
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
             'schedule_group': 'schedule-group-1',
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
             'schedule_group': 'schedule-group-1',
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
             'schedule_group': 'schedule-group-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         },
    )


class BaseTest(TestCase):

    app_label = 'testing'
    consent_catalogue_name = 'v1'

    def setUp(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        site_lab_tracker.autodiscover()
        TestAppConfiguration().prepare()
        VisitSchedule().build()
        self.test_visit_factory = TestVisitFactory
        self.study_site = StudySite.objects.all()[0]
        self.identity = '111111111'
        self.subject_identifier = '999-100000-1'
        self.visit_definition = VisitDefinition.objects.get(code='1000')
        self.registered_subject = RegisteredSubjectFactory(
            subject_identifier=self.subject_identifier)
        self.test_consent = TestConsentWithMixinFactory(
            registered_subject=self.registered_subject,
            gender=MALE,
            study_site=self.study_site,
            identity=self.identity,
            confirm_identity=self.identity,
            subject_identifier=self.subject_identifier)
        self.appointment_count = VisitDefinition.objects.all().count()
        self.appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=self.visit_definition)
