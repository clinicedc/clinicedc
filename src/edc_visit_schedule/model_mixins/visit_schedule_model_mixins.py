from django.db import models


from ..site_visit_schedules import site_visit_schedules


class VisitScheduleMethodsError(Exception):
    pass


class VisitScheduleModelMixinError(Exception):
    pass


class VisitScheduleMethodsModelMixin(models.Model):
    """A model mixin that adds methods used to work with the visit schedule.

    Declare with VisitScheduleFieldsModelMixin or the fields from
    VisitScheduleFieldsModelMixin
    """

    @property
    def visit(self):
        """Returns the visit object from the schedule object
        for this visit code.

        Note: This is not a model instance.
        """
        return self.visit_from_schedule

    @property
    def visit_from_schedule(self):
        """Returns the visit object from the schedule object
        for this visit code.

        Note: This is not a model instance.
        """
        visit = self.schedule.visits.get(self.visit_code)
        if not visit:
            raise VisitScheduleModelMixinError(
                f"Visit not found in schedule. Expected one of {self.schedule.visits}. "
                f"Got {self.visit_code}."
            )
        return visit

    @property
    def visits(self):
        """Returns all visit objects from the schedule object.
        """
        return self.schedule.visits

    @property
    def schedule(self):
        """Returns a schedule object from Meta.visit_schedule_name or
        self.schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'visit_schedule_name.schedule_name'
        """
        return self.visit_schedule.schedules.get(self.schedule_name)

    @property
    def visit_schedule(self):
        """Returns a visit schedule object from Meta.visit_schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'my_visit_schedule_name.my_schedule_name'

        or, for example, in the case of an offstudy model:
            visit_schedule_name = 'my_visit_schedule_name'
        """
        try:
            visit_schedule_name, _ = self._meta.visit_schedule_name.split(".")
        except ValueError:
            visit_schedule_name = self._meta.visit_schedule_name
        except AttributeError:
            visit_schedule_name = self.visit_schedule_name
        return site_visit_schedules.get_visit_schedule(
            visit_schedule_name=visit_schedule_name
        )

    class Meta:
        abstract = True


class VisitScheduleFieldsModelMixin(models.Model):
    """A model mixin that adds fields required to work with the visit
    schedule methods on the VisitScheduleMethodsModelMixin.

    Note: visit_code is not included.
    """

    visit_schedule_name = models.CharField(
        max_length=25,
        editable=False,
        help_text='the name of the visit schedule used to find the "schedule"',
    )

    schedule_name = models.CharField(max_length=25, editable=False)

    class Meta:
        abstract = True


class VisitCodeFieldsModelMixin(models.Model):
    visit_code = models.CharField(max_length=25, null=True, editable=False)

    visit_code_sequence = models.IntegerField(
        verbose_name="Sequence",
        default=0,
        null=True,
        blank=True,
        help_text=(
            "An integer to represent the sequence of additional "
            "appointments relative to the base appointment, 0, needed "
            "to complete data collection for the timepoint. (NNNN.0)"
        ),
    )

    class Meta:
        abstract = True


class VisitScheduleModelMixin(
    VisitScheduleFieldsModelMixin,
    VisitCodeFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
    models.Model,
):

    """A model mixin that adds adds field attributes and methods that
    link a model instance to its schedule.

    This mixin is used with Appointment and Visit models via their
    respective model mixins.
    """

    class Meta:
        abstract = True
