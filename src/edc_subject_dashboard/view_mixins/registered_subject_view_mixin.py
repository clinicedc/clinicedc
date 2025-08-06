from __future__ import annotations

from typing import Any

from edc_registration import get_registered_subject
from edc_registration.utils import valid_subject_identifier_or_raise


class RegisteredSubjectViewMixin:
    """Adds the subject_identifier to the context."""

    def __init__(self, **kwargs):
        self._subject_identifier: str | None = None
        self._registered_subject: str | None = None
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        # subject_identifier will only have value if passed in the url
        self._subject_identifier = kwargs.get("subject_identifier")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        if self.subject_identifier and valid_subject_identifier_or_raise(
            self.subject_identifier, raise_exception=True
        ):
            kwargs.update(
                subject_identifier=self.registered_subject.subject_identifier,
                gender=self.registered_subject.gender,
                dob=self.registered_subject.dob,
                initials=self.registered_subject.initials,
                identity=self.registered_subject.identity,
                firstname=self.registered_subject.first_name,
                lastname=self.registered_subject.last_name,
                registered_subject=self.registered_subject,
                registered_subject_pk=str(self.registered_subject.id),
            )
        return super().get_context_data(**kwargs)

    @property
    def subject_identifier(self):
        return self._subject_identifier

    @property
    def registered_subject(self):
        if not self._registered_subject:
            self._registered_subject = get_registered_subject(
                self.subject_identifier, raise_exception=True
            )
        return self._registered_subject
