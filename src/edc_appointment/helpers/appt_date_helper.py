from datetime import datetime
from dateutil.relativedelta import relativedelta

from edc_visit_schedule.models import VisitDefinition


class ApptDateTimeDescriptor(object):
    """For a registered_subject instance only"""
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value:
            if isinstance(value, datetime):
                self.value = value
            else:
                raise AttributeError('Can\'t set attribute \'registered_subject\'. Must be an instance of RegisteredSubject. Got %s.' % type(self.registered_subject))
        else:
            raise AttributeError("Can't set attribute registered_subject. Got none.")


class VisitDefintionDescriptor(object):
    """For a registered_subject instance only"""
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value:
            if isinstance(value, VisitDefinition):
                self.value = value
            else:
                raise AttributeError('Can\'t set attribute \'visit_deifinition\'. Must be an instance of VisitDefinition. Got %s.' % type(self.visit_definition))
        else:
            raise AttributeError("Can't set attribute visit_definition. Got none.")
    visit_definition = property(__get__, __set__)


class ApptDateHelper(object):

    appt_datetime = ApptDateTimeDescriptor()
    visit_definition = VisitDefintionDescriptor()

    def __init__(self, **kwargs):

        self.next_appt_datetime = None
        # base_appt_datetime = kwargs.get('base_appt_datetime')
        # visit_definition = kwargs.get('visit_definition')

    def set_next_appt_datetime(self, **kwargs):
        self.next_appt_datetime = None
        interval = self.visit_definition.base_interval
        unit = self.visit_definition.base_interval_unit
        if not interval == 0:
            if unit == 'Y':
                next_appt_datetime = self.appt_datetime + relativedelta(years=interval)
            elif unit == 'M':
                next_appt_datetime = self.appt_datetime + relativedelta(months=interval)
            elif unit == 'D':
                next_appt_datetime = self.appt_datetime + relativedelta(days=interval)
            elif unit == 'H':
                next_appt_datetime = self.appt_datetime + relativedelta(hours=interval)
            else:
                raise AttributeError("Cannot calculate net edc_appointment date, visit_definition.base_interval_unit must be Y,M,D or H. Got %s" % (unit,))
        return self.next_appt_datetime




