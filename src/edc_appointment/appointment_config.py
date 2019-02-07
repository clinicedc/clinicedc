from django.apps import apps as django_apps


class AppointmentConfigError(Exception):
    pass


class AppointmentConfig:

    default_appt_type = "clinic"

    def __init__(self, name=None, model=None, related_visit_model=None, appt_type=None):
        self.model = model
        self.name = name or self.model
        self.related_visit_model = related_visit_model
        try:
            self.related_visit_model_attr = self.related_visit_model.split(".")[1]
        except IndexError:
            self.related_visit_model_attr = self.related_visit_model
        self.appt_type = appt_type or self.default_appt_type

    def __repr__(self):
        return f"{self.__class__.__name__}({self.model}, {self.related_visit_model})"

    @property
    def model_cls(self):
        """Returns the appointment model class.
        """
        return django_apps.get_model(self.model)

    @property
    def related_visit_model_cls(self):
        """Returns the model class for the related visit model.
        """
        return getattr(
            self.model_cls, self.related_visit_model_attr
        ).related.related_model
