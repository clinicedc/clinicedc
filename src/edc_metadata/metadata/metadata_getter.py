from typing import Optional

from django.apps import apps as django_apps
from edc_appointment.stubs import AppointmentModelStub
from edc_visit_tracking.stubs import SubjectVisitModelStub


class MetadataGetter:

    """A class that gets a filtered queryset of metadata --
    `metadata_objects`.
    """

    metadata_model: Optional[str] = None

    def __init__(
        self,
        appointment: Optional[AppointmentModelStub] = None,
        subject_identifier: str = None,
        visit_code: str = None,
        visit_code_sequence: int = None,
    ) -> None:
        self.visit: Optional[SubjectVisitModelStub] = None
        try:
            self.visit = appointment.visit  # type:ignore
        except AttributeError:
            self.subject_identifier = subject_identifier
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
        else:
            self.subject_identifier = self.visit.subject_identifier
            self.visit_code = self.visit.visit_code
            self.visit_code_sequence = self.visit.visit_code_sequence
        self.metadata_objects = self.metadata_model_cls.objects.filter(
            **self.options
        ).order_by("show_order")

    @property
    def metadata_model_cls(self):
        return django_apps.get_model(self.metadata_model)

    @property
    def options(self):
        """Returns a dictionary of query options."""
        return dict(
            subject_identifier=self.subject_identifier,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
        )

    def next_object(self, show_order=None, entry_status=None):
        """Returns the next model instance based on the show order."""
        if show_order is None:
            metadata_obj = None
        else:
            opts = {"show_order__gt": show_order}
            if entry_status:
                opts.update(entry_status=entry_status)
            metadata_obj = self.metadata_objects.filter(**opts).order_by("show_order").first()
        return metadata_obj
