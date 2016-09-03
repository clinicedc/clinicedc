from datetime import timedelta

from django.apps import apps as django_apps

from .choices import VISIT_INTERVAL_UNITS
from .constants import HOUR, DAY, MONTH, YEAR
from .exceptions import VisitScheduleError
from .utils import get_lower_window_days, get_upper_window_days


class Panel:

    def __init__(self, panel_name=None, panel_type=None, aliquot_type_alpha_code=None):
        self.name = panel_name
        self.type = panel_type
        self.aliquot_type_code = aliquot_type_alpha_code

    def __str(self):
        return self.name


class Crf:
    def __init__(self, show_order, model=None, required=None, additional=None, **kwargs):
        self.show_order = show_order
        self._model = '{}.{}'.format(*model.split('.'))
        self.model_label_lower = model
        self.required = True if required is None else required
        self.additional = additional

    def __repr__(self):
        return '<Crf({}, {}, {})>'.format(self.show_order, self.model_label_lower, self.required)

    def __str__(self):
        return '{} {}'.format(self._model, 'Required' if self.required else '')

    @property
    def model(self):
        return django_apps.get_model(*self._model.split('.'))


class Requisition(Crf):

    def __init__(self, show_order, panel=None, **kwargs):
        super(Requisition, self).__init__(show_order, **kwargs)
        self.panel = panel

    def __repr__(self):
        return '<Requisition({}, {})>'.format(self.show_order, self.panel)

    def __str__(self):
        return '{} {}'.format(self.panel.name, 'Required' if self.required else '')


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
