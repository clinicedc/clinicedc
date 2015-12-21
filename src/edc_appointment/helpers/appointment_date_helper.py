import copy

from datetime import datetime, timedelta

from django.apps import apps as django_apps

from edc_configuration.models import GlobalConfiguration
from edc_visit_schedule.models import VisitDefinition
from edc_calendar import Calendar, Facility


class AppointmentDateHelper(object):
    """ """
    def __init__(self, suggested_appt_datetime, site_name):
        self.window_delta = None
        facility = Facility.objects.get(name=site_name)
        calendar = Calendar(facility=facility)
        appt_datetime = calendar.best_datetime(suggested_appt_datetime)
        


    def change_datetime(self, best_appt_datetime, new_appt_datetime, site, visit_definition):
        """Checks if an edc_appointment datetime from the user is OK to change."""
        new_appt_datetime = self.check_datetime(new_appt_datetime, site)
        if not visit_definition.is_datetime_in_window(new_appt_datetime, best_appt_datetime):
            new_appt_datetime = best_appt_datetime
        return new_appt_datetime

    def get_relative_datetime(self, base_appt_datetime, visit_definition):
        """ Returns edc_appointment datetime relative to the base_appointment_datetime."""
        appt_datetime = (
            base_appt_datetime + VisitDefinition.objects.relativedelta_from_base(visit_definition=visit_definition))
        return self.get_best_datetime(appt_datetime, base_appt_datetime.isoweekday())

    def check_datetime(self, appt_datetime, site):
        appt_datetime = self.check_if_allowed_isoweekday(appt_datetime)
        appt_datetime = self.check_if_holiday(appt_datetime)
        appt_datetime = self.move_on_appt_max_exceeded(appt_datetime, site)
        return appt_datetime

