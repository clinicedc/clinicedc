from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_lab')


class Requisition:

    def __init__(self, requisition):
        self._specimen_identifier = None
        self.object = requisition
        for field in self.object._meta.fields:
            if field.name != 'specimen_identifier':
                setattr(self, field.name, getattr(self.object, field.name))
        self._specimen_identifier = self.object.specimen_identifier
        self.specimen_type = app_config.aliquot_types[self.specimen_type]

    @property
    def specimen_identifier(self):
        return self._specimen_identifier

    @specimen_identifier.setter
    def specimen_identifier(self, value):
        self._specimen_identifier = value
        self.object.save()
