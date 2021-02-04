from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .constants import CLOSED_TIMEPOINT
from .timepoint import TimepointClosed


class TimepointLookup:

    """A class to be set as an attribute of a model
    controlled by a timepoint model.

    For example, a SubjectVisit model or a CrfModel. Verify that the
    default class attributes work for your model and timepoint model.
    If not, create a child class as has been done in the tests.

    Declare as:
        class CrfModel(...):

            timepoint_lookup_cls = TimepointLookup

            ...

    """

    timepoint_model = "edc_appointment.appointment"
    timepoint_related_model_lookup = "subject_visit__appointment"

    def __init__(self, timepoint_model=None, timepoint_related_model_lookup=None):
        self.timepoint_model = timepoint_model or self.timepoint_model
        self.timepoint_model_lookup = (
            timepoint_related_model_lookup or self.timepoint_related_model_lookup
        )

    def __str__(self):
        return self.timepoint_model

    @property
    def timepoint_model_cls(self):
        app_config = django_apps.get_app_config("edc_timepoint")
        return app_config.timepoints.get_model(self.timepoint_model)

    def raise_if_closed(self, model_obj=None):
        try:
            timepoint_obj = model_obj.__class__.objects.get(
                **{
                    f"{self.timepoint_related_model_lookup}"
                    "__timepoint_status": CLOSED_TIMEPOINT
                }
            )
        except ObjectDoesNotExist:
            pass
        else:
            raise TimepointClosed(f"Timepoint is closed for {model_obj}. See {timepoint_obj}.")
