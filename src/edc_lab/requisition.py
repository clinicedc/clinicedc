from edc_lab.site_labs import site_labs


class Requisition:
    """Wrapper class for the requisition model."""

    def __init__(self, requisition):
        self.object = requisition
        for field in self.object._meta.fields:
            if field.name not in ['specimen_identifier']:
                setattr(self, field.name, getattr(self.object, field.name))
        self.specimen_type = site_labs.get(self.object._meta.label_lower).aliquot_types[self.specimen_type]

    def __str__(self):
        return str(self.object)

    @property
    def specimen_identifier(self):
        return self.object.specimen_identifier

    @specimen_identifier.setter
    def specimen_identifier(self, value):
        self.object.specimen_identifier = value
        self.object.save()
        self.object = self.object.__class__.objects.get(requisition_identifier=self.requisition_identifier)
