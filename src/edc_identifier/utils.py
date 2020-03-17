import re

from django.apps import apps as django_apps
from edc_protocol import Protocol

from .exceptions import SubjectIdentifierError


def is_subject_identifier_or_raise(
    subject_identifier, reference_obj=None, raise_on_none=None
):
    """Returns the given subject identifier.

    * If the format of the `subject_identifier` is invalid,
      raises an exception.
    * If `subject_identifier` is None, does nothing, unless
      `raise_on_none` is `True`.
    """
    if subject_identifier or raise_on_none:
        if not re.match(
            Protocol().subject_identifier_pattern, subject_identifier or ""
        ):
            reference_msg = ""
            if reference_obj:
                reference_msg = f"See {repr(reference_obj)}. "
            raise SubjectIdentifierError(
                f"Invalid format for subject identifier. {reference_msg}"
                f"Got `{subject_identifier or ''}`. "
                f"Expected pattern `{Protocol().subject_identifier_pattern}`"
            )
    return subject_identifier
