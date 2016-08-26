from django.apps import apps as django_apps


class Timepoint:
    def __init__(self, model=None, datetime_field=None, status_field=None, closed_status=None):
        self.app_label, self.model_name = model.split('.')  # format label_lower
        self.datetime_field = datetime_field
        self.status_field = status_field
        self.closed_status = closed_status

    def __str__(self):
        return self.label_lower

    @property
    def model(self):
        return django_apps.get_model(self.app_label, self.model_name)

    @property
    def label_lower(self):
        return '{}.{}'.format(self.app_label, self.model_name)
