from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from django.core.exceptions import ObjectDoesNotExist
from edc_registration import get_registered_subject_model_cls

from edc_sites.get_site_model_cls import get_site_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class InvalidSiteForSubjectError(Exception):
    pass


class InvalidSubjectError(Exception):
    pass


def valid_site_for_subject_or_raise(
    subject_identifier: str, skip_get_current_site: bool | None = None
) -> Site:
    """Raises an InvalidSiteError exception if the subject_identifier is not
    from the current site.

    * Confirms by querying RegisteredSubject.
    * If subject_identifier is invalid will raise ObjectDoesNotExist
    """
    try:
        obj = get_registered_subject_model_cls().objects.get(
            subject_identifier=subject_identifier
        )
    except ObjectDoesNotExist:
        raise InvalidSubjectError(
            "Unknown subject. "
            f"Searched `{get_registered_subject_model_cls()._meta.label_lower}`. "
            f"Got subject_identifier=`{subject_identifier}`."
        )
    if skip_get_current_site:
        warn("Skipping validation of current site against registered subject site.")
        current_site = obj.site
    else:
        current_site = get_site_model_cls().objects.get_current()
        try:
            get_registered_subject_model_cls().objects.get(
                subject_identifier=subject_identifier, site=current_site
            )
        except ObjectDoesNotExist:
            raise InvalidSiteForSubjectError(
                f"Invalid site for subject. {subject_identifier}. Expected `{obj.site.name}`. "
                f"Got `{current_site.name}`"
            )
    return current_site
