from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from edc_registration import get_registered_subject
from edc_registration.utils import RegisteredSubjectDoesNotExist

from .get_site_model_cls import get_site_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class InvalidSiteForSubjectError(Exception):
    pass


def valid_site_for_subject_or_raise(
    subject_identifier: str, skip_get_current_site: bool | None = None
) -> Site:
    """Raises an InvalidSiteError exception if the subject_identifier is not
    from the current site.

    * Confirms by querying RegisteredSubject.
    * If subject_identifier is invalid will raise ObjectDoesNotExist
    """
    registered_subject = get_registered_subject(subject_identifier, raise_exception=True)
    if skip_get_current_site:
        warn("Skipping validation of current site against registered subject site.")
        current_site = registered_subject.site
    else:
        current_site = get_site_model_cls().objects.get_current()
        try:
            registered_subject = get_registered_subject(
                subject_identifier,
                site=current_site,
                raise_exception=True,
            )
        except RegisteredSubjectDoesNotExist:
            raise InvalidSiteForSubjectError(
                f"Invalid site for subject. {subject_identifier}. "
                f"Expected `{registered_subject.site.name}`. Got `{current_site.name}`"
            )
    return current_site
