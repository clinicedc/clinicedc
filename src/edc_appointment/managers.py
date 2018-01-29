from django.db import models
from django.db.models.deletion import ProtectedError

from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class AppointmentManagerError(Exception):
    pass


class AppointmentManager(models.Manager):

    def get_by_natural_key(self, subject_identifier, visit_schedule_name,
                           schedule_name, visit_code, visit_code_sequence):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence)

    def get_query_options(self, **kwargs):
        """Returns an options dictionary.

        Dictionary is based on the appointment instance or everything
        else.
        """
        appointment = kwargs.get('appointment')
        schedule_name = kwargs.get('schedule_name')
        subject_identifier = kwargs.get('subject_identifier')
        visit_schedule_name = kwargs.get('visit_schedule_name')
        options = dict(visit_code_sequence=0)
        try:
            options.update(
                subject_identifier=appointment.subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name)
        except AttributeError:
            options.update(subject_identifier=subject_identifier)
            try:
                visit_schedule_name, schedule_name = (
                    visit_schedule_name.split('.'))
                options.update(
                    visit_schedule_name=visit_schedule_name,
                    schedule_name=schedule_name)
            except ValueError:
                options.update(visit_schedule_name=visit_schedule_name)
            except AttributeError:
                pass
            if schedule_name and not visit_schedule_name:
                raise TypeError(
                    f'Expected visit_schedule_name for schedule_name '
                    f'\'{schedule_name}\'. Got {visit_schedule_name}')
            elif schedule_name:
                options.update(schedule_name=schedule_name)
        return options

    def get_visit_code(self, action, schedule, **kwargs):
        """Updates the options dictionary with the next or previous
        visit code in the schedule.

        if both visit_code and appointment are in kwargs visit_code
        takes precedence over apppointment.visit_code
        """
        visit_code = kwargs.get('visit_code')
        if not visit_code:
            try:
                appointment = kwargs.get('appointment')
                visit_code = appointment.visit_code
            except AttributeError:
                pass
        if action == 'next':
            visit = schedule.visits.next(visit_code)
        elif action == 'previous':
            visit = schedule.visits.previous(visit_code)
        else:
            raise AppointmentManagerError(
                f'Unknown action. Expected one of [next, previous]. Got \'{action}\'.')
        try:
            visit_code = visit.code
        except AttributeError:
            visit_code = None
        return visit_code

    def first_appointment(self, **kwargs):
        """Returns the first appointment instance for the given criteria.

        For visit_code_sequence=0.

        For example:
            first_appointment = (Appointment.objects.
                first_appointment(appointment=appointment))
        or:
            first_appointment = Appointment.objects.first_appointment(
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name)
        """
        options = self.get_query_options(**kwargs)
        try:
            first_appointment = self.filter(
                **options).order_by('timepoint')[0]
        except IndexError:
            first_appointment = None
        return first_appointment

    def last_appointment(self, **kwargs):
        """Returns the last appointment relative to the criteria.

        For visit_code_sequence=0.
        """
        options = self.get_query_options(**kwargs)
        try:
            last_appointment = [
                obj for obj in self.filter(**options).order_by(
                    'timepoint')][-1]
        except IndexError:
            last_appointment = None
        return last_appointment

    def next_appointment(self, **kwargs):
        """Returns the next appointment relative to the criteria or
        None if there is no next.

        For visit_code_sequence=0.

        Next is the next visit in a schedule, so schedule_name is required.

        For example:
            next_appointment = (Appointment.objects.
                first_appointment(appointment=appointment))
        or:
            next_appointment = Appointment.objects.first_appointment(
                visit_code=visit_code, appointment=appointment)
        or:
            next_appointment = Appointment.objects.first_appointment(
                visit_code=visit_code,
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name)
        """
        options = self.get_query_options(**kwargs)
        schedule = site_visit_schedules.get_visit_schedule(
            options.get('visit_schedule_name')).schedules.get(
                options.get('schedule_name'))
        options.update(
            visit_code=self.get_visit_code('next', schedule, **kwargs))
        try:
            next_appointment = self.filter(
                **options).order_by('timepoint')[0]
        except IndexError:
            next_appointment = None
        return next_appointment

    def previous_appointment(self, **kwargs):
        """Returns the previous appointment relative to the criteria
        or None if there is no previous.

        For visit_code_sequence=0.
        """
        options = self.get_query_options(**kwargs)
        schedule = site_visit_schedules.get_visit_schedule(
            options.get('visit_schedule_name')).schedules.get(
                options.get('schedule_name'))
        options.update(
            visit_code=self.get_visit_code('previous', schedule, **kwargs))
        try:
            previous_appointment = self.filter(
                **options).order_by('-timepoint')[0]
        except IndexError:
            previous_appointment = None
        return previous_appointment

    def delete_for_subject_after_date(self, subject_identifier, dt, op=None,
                                      visit_schedule_name=None,
                                      schedule_name=None):
        """Deletes appointments for a given subject_identifier with
        appt_datetime greater than `dt`.

        If a visit form exists for any appointment, a ProtectedError will
        be raised.
        """
        if not subject_identifier:
            raise TypeError('Expected value for subject_identifier. Got None')
        valid_ops = ['gt', 'gte']
        op = 'gte' if op is None else op
        if op not in valid_ops:
            raise TypeError('Allowed lookup operators are {}. Got {}.'.format(
                ', '.join(valid_ops), op))
        options = {
            'subject_identifier': subject_identifier,
            f'appt_datetime__{op}': dt}
        if schedule_name and not visit_schedule_name:
            raise TypeError(
                f'Expected visit_schedule_name for schedule_name '
                f'\'{schedule_name}\'. Got {visit_schedule_name}')
        if visit_schedule_name:
            try:
                visit_schedule_name, schedule_name = visit_schedule_name.split(
                    '.')
            except ValueError:
                if schedule_name:
                    options.update(dict(schedule_name=schedule_name))
            options.update(dict(visit_schedule_name=visit_schedule_name))
        deleted = 0
        appointments = self.filter(**options).order_by('-timepoint')
        for appointment in appointments:
            try:
                appointment.delete()
                deleted += 1
            except ProtectedError:
                break
        return deleted
