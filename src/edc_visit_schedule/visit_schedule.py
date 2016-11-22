import re

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from .exceptions import AlreadyRegistered, VisitScheduleError


class VisitSchedule:

    def __init__(self, name, app_label, default_enrollment_model=None, default_disenrollment_model=None, visit_model=None,
                 offstudy_model=None, death_report_model=None, verbose_name=None):
        self.name = name
        if not re.match(r'[a-z0-9\_\-]+$', name):
            raise ImproperlyConfigured('Visit schedule name may only contains numbers, lower case letters and \'_\'.')
        self.app_label = app_label
        self.verbose_name = verbose_name or ' '.join([s.capitalize() for s in name.split('_')])
        self.death_report_model = None
        self.default_disenrollment_model = None
        self.default_enrollment_model = None
        self.offstudy_model = None
        self.offstudy_model = None
        self.visit_model = None
        self.add_offstudy_model(offstudy_model)
        self.add_visit_model(visit_model)
        if default_disenrollment_model:
            self.add_default_disenrollment_model(default_disenrollment_model)
        if default_enrollment_model:
            self.add_default_enrollment_model(default_enrollment_model)
        if death_report_model:
            self.add_death_report_model(death_report_model)
        self.schedules = {}

    def __repr__(self):
        return '<VisitSchedule(\'{}\', \'{}\')>'.format(self.name, self.app_label)

    def __str__(self):
        return self.verbose_name

    def add_schedule(self, schedule):
        """Add a schedule if not already added."""
        if schedule.name in self.schedules:
            raise AlreadyRegistered('A schedule with name {} is already registered'.format(schedule.name))
        schedule.enrollment_model = schedule.enrollment_model or self.default_enrollment_model
        self.validate_model_for_schedule(schedule, 'enrollment_model')
        schedule.disenrollment_model = schedule.disenrollment_model or self.default_disenrollment_model
        self.validate_model_for_schedule(schedule, 'disenrollment_model')
        schedule.offstudy_model = self.offstudy_model
        schedule.visit_model = self.visit_model
        if self.death_report_model:
            schedule.death_report_model = self.death_report_model
        self.schedules.update({schedule.name: schedule})
        return schedule

    def get_schedule(self, value=None):
        """Return a schedule by name, by enrollment model or by the enrollment model label_lower."""
        try:
            _, _ = value.split('.')
            enrollment_model = django_apps.get_model(*value.split('.'))
        except ValueError:
            return self.schedules.get(value)
        except AttributeError:
            value._meta
            enrollment_model = value
        for schedule in self.schedules.values():
            if schedule.enrollment_model == enrollment_model:
                return schedule
        return None

    def add_default_enrollment_model(self, model):
        self.default_enrollment_model = django_apps.get_model(*model.split('.'))
        try:
            self.default_enrollment_model.create_appointments
        except AttributeError as e:
            raise ImproperlyConfigured(
                '\'{}\' cannot be an enrollment model. It is not configured '
                'to create appointments. Got {}'.format(model._meta.label_lower, str(e)))
        self.validate_modelmixin_attrs(self.default_enrollment_model)

    def add_default_disenrollment_model(self, model):
        self.default_disenrollment_model = django_apps.get_model(*model.split('.'))
        self.validate_modelmixin_attrs(self.default_disenrollment_model)

    def add_death_report_model(self, model):
        self.death_report_model = django_apps.get_model(*model.split('.'))

    def add_offstudy_model(self, model):
        self.offstudy_model = django_apps.get_model(*model.split('.'))

    def add_visit_model(self, model):
        self.visit_model = django_apps.get_model(*model.split('.'))

    def validate_model_for_schedule(self, schedule, attrname):
        model = getattr(schedule, attrname)
        try:
            visit_schedule_name, schedule_name = model._meta.visit_schedule_name.split('.')
        except AttributeError as e:
            if '_meta' in str(e):
                raise VisitScheduleError(
                    'Cannot register schedule \'{}\'. Model \'{}\' has not been set. '
                    'Either set this explicitly on the schedule or set a \'default_{}\' '
                    'on visit schedule \'{}\'.'.format(
                        schedule.name, attrname, attrname, self.name))
            else:
                raise AttributeError(e)
        except ValueError:
            visit_schedule_name = model._meta.visit_schedule_name
            schedule_name = None
        if visit_schedule_name != self.name:
            raise VisitScheduleError(
                'Cannot register schedule. Model \'{}\' does not belong to this visit schedule. '
                'Got \'{}\' != \'{}\''.format(model._meta.label_lower, self.name, visit_schedule_name))
        if schedule_name and schedule_name != schedule.name:
            raise VisitScheduleError(
                'Cannot register schedule. Model \'{}\' does not belong to this schedule. '
                'Got \'{}\' != \'{}\''.format(model._meta.label_lower, schedule.name, schedule_name))

    def validate_modelmixin_attrs(self, model):
        """Validate that the attrs from the enrollment/disenrollment model_mixins exist."""
        try:
            getattr(getattr(model, '_meta'), 'visit_schedule_name')
        except AttributeError as e:
                raise ImproperlyConfigured(
                    '\'{}\' for schedule \'{}\' is missing \'_meta\' attribute \''
                    'visit_schedule_name\'. Got {} [{}].'.format(
                        model._meta.label_lower, self.name, str(e), model))
        field_required = ['report_datetime', 'schedule_name']
        field_found = [f.name for f in model._meta.fields if f.name in ['report_datetime', 'schedule_name']]
        field_missing = [f for f in field_required if f not in field_found]
        if field_missing:
            raise ImproperlyConfigured(
                '\'{}\' for schedule \'{}\' is missing field \'{}\''.format(
                    model._meta.label_lower, self.name, field_missing[0]))
