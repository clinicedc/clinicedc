from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from edc_registration import get_registered_subject
from edc_registration.utils import RegisteredSubjectDoesNotExist

from ..exceptions import InvalidSiteForSubjectError
from .get_site_model_cls import get_site_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

    from edc_registration.models import RegisteredSubject

__all__ = ["valid_site_for_subject_or_raise"]


def valid_site_for_subject_or_raise(
    subject_identifier: str, skip_get_current_site: bool | None = None
) -> Site:
    """Raises an InvalidSiteError exception if the subject_identifier is not
    from the current site.

    * Confirms by querying RegisteredSubject.
    * If subject_identifier is invalid will raise ObjectDoesNotExist
    """
    registered_subject: RegisteredSubject | None = get_registered_subject(
        subject_identifier, raise_exception=True
    )
    if skip_get_current_site:
        warn("Skipping validation of current site against registered subject site.")
        site_obj = registered_subject.site
    else:
        site_obj: Site = get_site_model_cls().objects.get_current()
        try:
            get_registered_subject(
                subject_identifier,
                site=site_obj,
                raise_exception=True,
            )
        except RegisteredSubjectDoesNotExist:
            if not registered_subject.site_id:
                raise InvalidSiteForSubjectError(
                    "Site not defined for registered subject! "
                    f"Subject identifier=`{subject_identifier}`. "
                )
            raise InvalidSiteForSubjectError(
                f"Invalid site for subject. Subject identifier=`{subject_identifier}`. "
                f"Expected `{registered_subject.site.name}`. "
                f"Got site_id=`{site_obj.id}`"
            )
    return site_obj
