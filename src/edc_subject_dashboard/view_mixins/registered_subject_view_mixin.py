import re

from django.core.exceptions import ObjectDoesNotExist
from edc_protocol import Protocol
from edc_registration.models import RegisteredSubject, RegisteredSubjectError
from edc_sites.permissions import may_view_other_sites


class RegisteredSubjectViewMixin:

    """Adds the subject_identifier to the context."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get(self, request, *args, **kwargs):
        self.subject_identifier = kwargs.get("subject_identifier")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.subject_identifier:
            if not re.match(Protocol().subject_identifier_pattern, self.subject_identifier):
                raise RegisteredSubjectError(
                    f"Invalid subject identifier format. "
                    f"Valid pattern is `{Protocol().subject_identifier_pattern}`. "
                    f"See `edc_protocol.Protocol().subject_identifier_pattern`. "
                    f"Got `{self.subject_identifier}`."
                )
            if may_view_other_sites(self.request):
                manager = RegisteredSubject.objects
            else:
                manager = RegisteredSubject.on_site
            try:
                obj = manager.get(subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                try:
                    RegisteredSubject.objects.get(subject_identifier=self.subject_identifier)
                except ObjectDoesNotExist:
                    raise RegisteredSubjectError(
                        f"Invalid subject identifier. Got {self.subject_identifier}."
                    )
                else:
                    context.update(subject_identifier=self.subject_identifier)
            else:
                context.update(
                    subject_identifier=obj.subject_identifier,
                    gender=obj.gender,
                    dob=obj.dob,
                    initials=obj.initials,
                    identity=obj.identity,
                    firstname=obj.first_name,
                    lastname=obj.last_name,
                    registered_subject=obj,
                    registered_subject_pk=str(obj.pk),
                )
        return context
