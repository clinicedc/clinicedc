from django.apps import apps as django_apps
from edc_lab.site_lab_profiles import site_lab_profiles

app_config = django_apps.get_app_config('edc_lab')


class Requisition:

    model = app_config.requisition_model

    def __init__(self, requisition):
        self.object = requisition
        for field in self.object._meta.fields:
            if field.name not in ['specimen_identifier']:
                setattr(self, field.name, getattr(self.object, field.name))
        self.specimen_type = site_lab_profiles.get(self.object._meta.label_lower).aliquot_types[self.specimen_type]

    def __str__(self):
        return str(self.object)

    @property
    def specimen_identifier(self):
        return self.object.specimen_identifier

    @specimen_identifier.setter
    def specimen_identifier(self, value):
        self.object.specimen_identifier = value
        self.object.save()
        self.object = self.model.objects.get(requisition_identifier=self.requisition_identifier)
