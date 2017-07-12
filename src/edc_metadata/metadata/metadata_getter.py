from django.core.exceptions import ObjectDoesNotExist


class MetadataGetter:

    """A class that gets a filtered queryset of metadata --
    `metadata_objects`.
    """

    metadata_model_cls = None

    def __init__(self, appointment=None, subject_identifier=None, visit_code=None):
        try:
            self.visit = appointment.visit
        except (AttributeError, ObjectDoesNotExist):
            self.visit = None
        if self.visit:
            self.subject_identifier = self.visit.subject_identifier
            self.visit_code = self.visit.visit_code
        else:
            self.subject_identifier = subject_identifier
            self.visit_code = visit_code
        self.metadata_objects = self.metadata_model_cls.objects.filter(
            **self.options).order_by('show_order')

    @property
    def options(self):
        return dict(
            subject_identifier=self.subject_identifier,
            visit_code=self.visit_code)
