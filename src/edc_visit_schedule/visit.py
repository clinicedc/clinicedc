from datetime import timedelta
from django.apps import apps as django_apps

from .utils import get_lower_window_days, get_upper_window_days
from .choices import VISIT_INTERVAL_UNITS
from .exceptions import VisitScheduleError


# def is_visit_tracking_model(value):
#     from edc_visit_tracking.models import VisitModelMixin
#     content_type_map = ContentTypeMap.objects.get(pk=value)
#     if not issubclass(content_type_map.model_class(), VisitModelMixin):
#         raise ValidationError('Select a model that is a subclass of VisitModelMixin')

class Panel:

    def __init__(self, panel_name=None, panel_type=None, aliquot_type_alpha_code=None):
        self.name = panel_name
        self.type = panel_type
        self.aliquot_type_code = aliquot_type_alpha_code

    def __str(self):
        return self.name


class Crf:
    def __init__(self, show_order, model=None, app_label=None, model_name=None, is_required=None, is_additional=None):
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

    def __init__(self, show_order, panel_name=None, panel_type=None, aliquot_type_alpha_code=None, **kwargs):
        super(Requisition, self).__init__(show_order, **kwargs)
        self.panel = Panel(panel_name, panel_type, aliquot_type_alpha_code)


class Visit:

    def __init__(self, code, title, visit_model, schedule, **kwargs):
        self.code = code  # unique
        self.title = title
        self.visit_model = visit_model
        self.schedule = schedule  # Visit definition may be used in more than one schedule
        self.insructions = kwargs.get('instructions')
        self.time_point = kwargs.get('time_point', 0)
        self.base_interval = kwargs.get('base_interval', 0)  # 'Interval from base timepoint 0 as an integer.'
        self.base_interval_unit = kwargs.get('base_interval', 'D')  # choices = VISIT_INTERVAL_UNITS
        if self.base_interval_unit not in [item[0] for item in VISIT_INTERVAL_UNITS]:
            raise VisitScheduleError('Invalid interval unit')
        self.lower_window = kwargs.get('lower_window', 0)
        self.lower_window_unit = kwargs.get('lower_window_unit', 'D')
        self.upper_window = kwargs.get('upper_window', 0)
        self.upper_window_unit = kwargs.get('upper_window_unit', 'D')
        self.grouping = kwargs.get('grouping')
        self.crfs = kwargs.get('crfs')
        self.requisitions = kwargs.get('requisitions')

    def visit_tracking_content_type_map(self):
        return self.visit_model

    def get_rdelta_attrname(self, unit):
        if unit == 'H':
            rdelta_attr_name = 'hours'
        elif unit == 'D':
            rdelta_attr_name = 'days'
        elif unit == 'M':
            rdelta_attr_name = 'months'
        elif unit == 'Y':
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
