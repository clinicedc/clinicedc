from collections import OrderedDict
from edc_constants.constants import REQUIRED, NOT_ADDITIONAL
from edc_visit_schedule.classes import (
    VisitScheduleConfiguration, CrfTuple, RequisitionPanelTuple, MembershipFormTuple, ScheduleTuple)
from edc_testing.models import TestVisit2, TestConsentWithMixin, TestAliquotType, TestPanel

from .test_models import TestVisitModel1


entries = (
    CrfTuple(10L, u'edc_export', u'testcrfmodel1', REQUIRED, NOT_ADDITIONAL),
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
        'schedule-1': MembershipFormTuple('schedule-1', TestConsentWithMixin, True),
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
            'visit_tracking_model': TestVisitModel1,
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
             'visit_tracking_model': TestVisitModel1,
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
             'visit_tracking_model': TestVisit2,
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
             'visit_tracking_model': TestVisit2,
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
             'visit_tracking_model': TestVisit2,
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
             'visit_tracking_model': TestVisit2,
             'schedule': 'schedule-1',
             'instructions': None,
            'requisitions': requisitions,
            'entries': entries},
         },
    )
