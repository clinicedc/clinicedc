from django.db import models

from .visit_code_fields_model_mixin import VisitCodeFieldsModelMixin
from .visit_schedule_fields_model_mixin import VisitScheduleFieldsModelMixin
from .visit_schedule_methods_model_mixin import VisitScheduleMethodsModelMixin


class VisitScheduleModelMixin(
    VisitScheduleFieldsModelMixin,
    VisitCodeFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
    models.Model,
):

    """A model mixin for Appointment and related (subject) visit models.

    A model mixin that adds field attributes and methods that
    link a model instance to its schedule.

    This mixin is used with Appointment and Visit models via their
    respective model mixins.
    """

    class Meta:
        abstract = True
