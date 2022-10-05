from django.apps import apps as django_apps

from .timepoint import Timepoint


class TimepointDoesNotExist(Exception):
    pass


class TimepointConfigError(Exception):
    pass


class TimepointCollection:

    """Contains a collection of Timepoint instances."""

    def __init__(self, timepoints=None):
        self._timepoints = {}
        for timepoint in timepoints:
            self.add(**timepoint.__dict__)

    def __iter__(self):
        return iter(self._timepoints)

    def add(self, model=None, **kwargs):
        self._timepoints.update({model: Timepoint(model=model, **kwargs)})

    def get_model(self, model=None):
        """Returns the timepoint's model class."""
        timepoint = self.get(model)
        return django_apps.get_model(timepoint.model)

    def get(self, model=None):
        """Returns the timepoint class for this model."""
        try:
            timepoint = self._timepoints[model]
        except KeyError:
            raise TimepointDoesNotExist(
                f"No timepoint has been configured with {model}. "
                "See AppConfig for edc_timepoint. Hint: Perhaps you are using a custom "
                "`Appointment` model?"
            )
        return timepoint
