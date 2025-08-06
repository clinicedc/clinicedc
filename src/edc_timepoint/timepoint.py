from django.apps import apps as django_apps


class TimepointClosed(Exception):
    pass


class Timepoint:
    """A class that represents a timepoint model and the relevant
    attributes and values of that model.

    Note: typically `model` is `edc_appointment.appointment`.
    """

    def __init__(self, model=None, datetime_field=None, status_field=None, closed_status=None):
        self.model = model
        self.datetime_field = datetime_field
        self.status_field = status_field
        self.closed_status = closed_status

    def __str__(self):
        return self.model

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)
