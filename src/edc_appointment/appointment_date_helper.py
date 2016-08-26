import copy

from datetime import datetime, timedelta

from django.apps import apps as django_apps

from .models import Holiday
from .window_period_helper import WindowPeriodHelper
from dateutil.relativedelta import relativedelta


class AppointmentDateHelper(object):
    """ """
    def __init__(self, *args):
        app_config = django_apps.get_app_config('edc_appointment')
        self.appointment_model = app_config.model
        self.window_delta = None
        # not used
        self.allow_backwards = False
        self.appointments_days_forward = app_config.appointments_days_forward
        self.appointments_per_day_max = app_config.appointments_per_day_max
        self.use_same_weekday = app_config.use_same_weekday
        self.weekday = app_config.weekday
        self.allowed_iso_weekdays = app_config.allowed_iso_weekdays

    def get_best_datetime(self, appt_datetime, weekday=None, exception_cls=None):
        """ Gets the appointment datetime on insert.

        For example, may be configured to be on the same day as the base, not on holiday, etc.

        Note, appt_datetime comes from the enrollment model's registration_datetime"""
        exception_cls = exception_cls or AttributeError
        weekday = weekday or self.weekday
        if weekday and self.use_same_weekday:
            appt_datetime = self.move_appt_to_same_weekday(appt_datetime, weekday)
        appt_datetime = self.check_appt_date(appt_datetime)
        return appt_datetime

    def change_datetime(self, best_appt_datetime, new_appt_datetime, visit_schedule, visit_code):
        """Checks if an appointment datetime from the user is OK to accept."""
        window_period = WindowPeriodHelper(visit_schedule, visit_code, best_appt_datetime, new_appt_datetime)
        appt_datetime = self.check_appt_date(new_appt_datetime)
        if not window_period.check_datetime():
            # return unchanged appt_datetime
            appt_datetime = best_appt_datetime
        if not appt_datetime:
            raise TypeError('Appt_datetime cannot be None')
        return appt_datetime

    def check_appt_date(self, appt_datetime):
        """Return appointment date time is not a holiday, isoweekday is allowed and no maximum appointments reached."""
        original_appt_datetime = copy.copy(appt_datetime)
        appt_datetime = self.check_if_allowed_isoweekday(appt_datetime)
        appt_datetime = self.check_if_holiday(appt_datetime)
#         appt_datetime_max_day = self.move_on_appt_max_exceeded(appt_datetime_holiday)
#         if appt_datetime_weekday == appt_datetime_holiday == appt_datetime_max_day:
#             new_appt_date = copy.deepcopy(appt_datetime_max_day)
#         else:
#             appt_datetime_weekday = self.check_if_allowed_isoweekday(appt_datetime_max_day)
#             appt_datetime_holiday = self.check_if_holiday(appt_datetime_weekday)
#             appt_datetime_max_day = self.move_on_appt_max_exceeded(appt_datetime_holiday)
#             # Recurse to get the same date from all 3 methods
#             self.check_appt_date(appt_datetime_max_day)
        return appt_datetime or original_appt_datetime

    def check_if_allowed_isoweekday(self, appt_datetime):
        """ Checks if weekday is allowed, otherwise adjust forward or backward """
        allowed_iso_weekdays = [int(num) for num in str(self.allowed_iso_weekdays)]
        if appt_datetime.isoweekday() not in allowed_iso_weekdays:
            forward = copy.deepcopy(appt_datetime)
            while forward.isoweekday() not in allowed_iso_weekdays:
                forward = forward + timedelta(days=+1)
            backward = copy.deepcopy(appt_datetime)
            while backward.isoweekday() not in allowed_iso_weekdays:
                backward = backward + timedelta(days=-1)
            # which is closer to the original appt_datetime
            td_forward = abs(appt_datetime - forward)
            td_backward = abs(appt_datetime - backward)
            if td_forward <= td_backward:
                appt_datetime = forward
            else:
                appt_datetime = backward
        if not appt_datetime:
            raise TypeError('Appt_datetime cannot be None')
        return appt_datetime

    def check_if_holiday(self, appt_datetime):
        """ Checks if appt_datetime lands on a holiday, if so, move forward """
        while True:
            try:
                Holiday.objects.get(holiday_date=appt_datetime.date())
                appt_datetime = appt_datetime + relativedelta(days=1)
            except Holiday.DoesNotExist:
                return appt_datetime
        return appt_datetime

    def move_appt_to_same_weekday(self, appt_datetime, weekday=1):
        """ Moves appointment to use same weekday for each subject appointment."""
        original_appt_datetime = copy.copy(appt_datetime)
        if self.use_same_weekday:
            if weekday not in range(1, 8):
                raise ValueError('Weekday must be a number between 1-7, Got %s' % (weekday, ))
            # make all appointments land on the same isoweekday,
            # if possible as date may change because of holiday and/or iso_weekday checks below)
            forward = appt_datetime
            while not forward.isoweekday() == weekday:
                forward = forward + timedelta(days=+1)
            backward = appt_datetime
            while not backward.isoweekday() == weekday:
                backward = backward - timedelta(days=+1)
            # which is closer to the original appt_datetime
            td_forward = abs(appt_datetime - forward)
            td_backward = abs(appt_datetime - backward)
            if td_forward <= td_backward:
                appt_datetime = forward
            else:
                appt_datetime = backward
        return appt_datetime or original_appt_datetime

#     def move_on_appt_max_exceeded(self, appt_datetime):
#         """Moves appointment date to another date if the appointments_per_day_max is exceeded."""
#         # get a list of appointments in the date range from 'appt_datetime' to 'appt_datetime'+days_forward
#         # use model field appointment.best_appt_datetime not appointment.appt_datetime
#         # TODO: change this query to allow the search to go to the beginning of the week
#         original_appt_datetime = copy(appt_datetime)
#         appointments = self.appointment_model.objects.filter(
#             best_appt_datetime__gte=appt_datetime,
#             best_appt_datetime__lte=appt_datetime + timedelta(days=self.appointments_days_forward))
#         if appointments:
#             # looking for appointments per day
#             # create dictionary of { day: count, ... }
#             appt_dates = [appointment.appt_datetime.date() for appointment in appointments]
#             appt_date_counts = dict((i, appt_dates.count(i)) for i in appt_dates)
#             if not appt_date_counts.get(my_appt_date) or appt_date_counts.get(my_appt_date) < self.appointments_per_day_max:
#                 appt_date = my_appt_date
#             else:
#                 count = 0
#                 while count < self.appointments_days_forward:
#                     # look for an alternative date
#                     appt_date += timedelta(days=1)
#                     if (not appt_date_counts.get(appt_date) or
#                             appt_date_counts.get(appt_date) < self.appointments_per_day_max):
#                         self.message = 'Appointment date has been moved to {0}.'.format(appt_date)
#                         break
#                     count += 1
#             # return an appointment datetime that uses the time from the originally desrired datetime
#             appt_datetime = datetime(
#                 appt_date.year, appt_date.month, appt_date.day, appt_datetime.hour, appt_datetime.minute)
#         return appt_datetime or original_appt_datetime
