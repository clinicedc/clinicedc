import inspect

from dateutil.relativedelta import relativedelta

from django.db import models


class VisitDefinitionManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)

    def next_visit_definition(self, **kwargs):
        """Returns next visit_definition for the given visit_definition. """

        if kwargs.get('visit_definition'):
            visit_definition = kwargs.get('visit_definition')
            schedule = visit_definition
        elif kwargs.get('schedule') and kwargs.get('code'):
            schedule = kwargs.get('schedule')
            code = kwargs.get('code')
            if super(VisitDefinitionManager, self).filter(schedule=schedule, code=code):
                visit_definition = super(VisitDefinitionManager, self).get(
                    schedule=schedule, code=code)
            else:
                raise ValueError(
                    '%s method %s cannot determine the visit_definition given '
                    ' schedule=\'%s\' and code=\'%s\'' % (
                        self.__name__, inspect.stack()[0][3], schedule, code))
        else:
            raise AttributeError('%s method %s requires a visit_definition instance OR schedule '
                                 'and code' % (self.__name__, inspect.stack()[0][3], ))

        visit_definitions = super(VisitDefinitionManager, self).filter(
            schedule=visit_definition.schedule).exclude(
                id=visit_definition.id).order_by('time_point')

        if visit_definitions:
            next_visit_def = visit_definitions[0]
        else:
            next_visit_def = None
        return next_visit_def

    def list_all_for_model(self, registered_subject, model_name):
        """Lists all visit_definitions for which appointments
        would be created or updated for this model_name."""
        Schedule = models.get_model('edc_visit_schedule', 'schedulegroup')
        if Schedule.objects.filter(membership_form__content_type_map__model=model_name):
            # get list of visits for scheduled group containing this model
            visit_definitions = super(VisitDefinitionManager, self).filter(
                schedule=Schedule.objects.get(membership_form__content_type_map__model=model_name))
        else:
            visit_definitions = []
        return visit_definitions

    def relativedelta_from_base(self, **kwargs):
        """Returns the relativedelta from the zero time_point visit_definition."""

        if kwargs.get('visit_definition'):
            visit_definition = kwargs.get('visit_definition')
        else:
            raise AttributeError(
                '%s method %s requires a visit_definition instance' % (
                    self.__name__, inspect.stack()[0][3],))
        interval = visit_definition.base_interval
        unit = visit_definition.base_interval_unit
        if interval == 0:
            rdelta = relativedelta(days=0)
        else:
            if unit == 'Y':
                rdelta = relativedelta(years=interval)
            elif unit == 'M':
                rdelta = relativedelta(months=interval)
            elif unit == 'D':
                rdelta = relativedelta(days=interval)
            elif unit == 'H':
                rdelta = relativedelta(hours=interval)
            else:
                raise AttributeError(
                    "Cannot calculate relativedelta, visit_definition.base_interval_unit "
                    "must be Y,M,D or H. Got %s" % (unit, ))
        return rdelta
