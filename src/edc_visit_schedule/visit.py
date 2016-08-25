from datetime import timedelta
from django.apps import apps as django_apps

from .utils import get_lower_window_days, get_upper_window_days
from .constants import HOUR, DAY, MONTH, YEAR
from .choices import VISIT_INTERVAL_UNITS
from .exceptions import VisitScheduleError
from edc_visit_schedule.exceptions import VisitError


class Panel:

    def __init__(self, panel_name=None, panel_type=None, aliquot_type_alpha_code=None):
        self.name = panel_name
        self.type = panel_type
        self.aliquot_type_code = aliquot_type_alpha_code

    def __str(self):
        return self.name


class Crf:
    def __init__(self, show_order, model=None, app_label=None, model_name=None,
                 is_required=None, is_additional=None, **kwargs):
        self.show_order = show_order
        if model:
            self.model = model
            self.app_label = model._meta.app_label
            self.model_name = model._meta.model_name
        else:
            self.app_label = app_label
            self.model_name = model_name
            self.model = django_apps.get_model(self.app_label, self.model_name)
        self.is_required = True if is_required is None else is_required
        self.is_additional = is_additional


class Requisition(Crf):

    def __init__(self, show_order, panel_name=None, panel_type=None,
                 aliquot_type_alpha_code=None, **kwargs):
        super(Requisition, self).__init__(show_order, **kwargs)
        self.panel = Panel(panel_name, panel_type, aliquot_type_alpha_code)


class Visit:

    def __init__(self, code, **kwargs):
        self.code = code  # unique
        self.title = kwargs.get('title', 'Visit {}'.format(code))
        self.insructions = kwargs.get('instructions')
        self.timepoint = kwargs.get('timepoint', 0)
        self.base_interval = kwargs.get('base_interval', self.timepoint)
        self.base_interval_unit = kwargs.get('base_interval_unit', DAY)  # choices = VISIT_INTERVAL_UNITS
        if self.base_interval_unit not in [item[0] for item in VISIT_INTERVAL_UNITS]:
            raise VisitScheduleError('Invalid interval unit. Got \'{}\''.format(self.base_interval_unit))
        self.lower_window = kwargs.get('lower_window', 0)
        self.lower_window_unit = kwargs.get('lower_window_unit', DAY)
        self.upper_window = kwargs.get('upper_window', 0)
        self.upper_window_unit = kwargs.get('upper_window_unit', DAY)
        self.grouping = kwargs.get('grouping')
        self.crfs = kwargs.get('crfs')
        self.requisitions = kwargs.get('requisitions')

    def __repr__(self):
        return 'Visit({}, {})'.format(self.code, self.timepoint)

    def get_rdelta_attrname(self, unit):
        if unit == HOUR:
            rdelta_attr_name = 'hours'
        elif unit == DAY:
            rdelta_attr_name = 'days'
        elif unit == MONTH:
            rdelta_attr_name = 'months'
        elif unit == YEAR:
            rdelta_attr_name = 'years'
        else:
            raise TypeError('Unknown value for visit_definition.upper_window_unit. '
                            'Expected [H, D, M, Y]. Got {0}.'.format(unit))
        return rdelta_attr_name

    def get_lower_window_datetime(self, appt_datetime):
        if not appt_datetime:
            return None
        days = get_lower_window_days(self.lower_window, self.lower_window_unit)
        td = timedelta(days=days)
        return appt_datetime - td

    def get_upper_window_datetime(self, appt_datetime):
        if not appt_datetime:
            return None
        days = get_upper_window_days(self.upper_window, self.upper_window_unit)
        td = timedelta(days=days)
        return appt_datetime + td
