from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.utils.translation import gettext as _

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionNotConfiguredForUpdate,
    NotConsentedError,
    SiteConsentError,
)
from edc_consent.site_consents import site_consents
from edc_form_validators import INVALID_ERROR
from edc_sites.site import sites as site_sites

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class ConsentDefinitionFormValidatorMixin:

    @property
    def subject_consent(self):
        cdef = self.get_consent_definition()
        return cdef.model_cls.objects.get(subject_identifier=self.subject_identifier)

    def get_consent_datetime_or_raise(
        self,
        report_datetime: datetime = None,
        site: Site = None,
        fldname: str = None,
        error_code: str = None,
    ) -> datetime:
        """Returns the consent_datetime of this subject"""
        consent_obj = self.get_consent_or_raise(
            report_datetime=report_datetime,
            site=site,
            fldname=fldname,
            error_code=error_code,
        )
        return consent_obj.consent_datetime

    def get_consent_or_raise(
        self,
        report_datetime: datetime = None,
        site: Site = None,
        fldname: str | None = None,
        error_code: str | None = None,
    ) -> datetime:
        """Returns the consent_datetime of this subject.

        Wraps func `consent_datetime_or_raise` to re-raise exceptions
        as ValidationError.
        """

        fldname = fldname or "report_datetime"
        error_code = error_code or INVALID_ERROR
        try:
            consent_obj = site_consents.get_consent_or_raise(
                subject_identifier=self.subject_identifier,
                report_datetime=report_datetime,
                site_id=getattr(site, "id", None),
            )
        except (NotConsentedError, ConsentDefinitionNotConfiguredForUpdate) as e:
            self.raise_validation_error({fldname: str(e)}, error_code)
        return consent_obj

    def get_consent_definition(
        self,
        report_datetime: datetime = None,
        fldname: str = None,
        error_code: str = None,
    ) -> ConsentDefinition:
        # get the consent definition (must be from this schedule)
        schedule = getattr(self, "related_visit", self.instance).schedule

        site = getattr(self, "related_visit", self.instance).site
        try:
            consent_definition = schedule.get_consent_definition(
                site=site_sites.get(site.id),
                report_datetime=report_datetime,
            )
        except ConsentDefinitionDoesNotExist as e:
            self.raise_validation_error({fldname: str(e)}, error_code)
        except SiteConsentError:
            possible_consents = "', '".join(
                [cdef.display_name for cdef in site_consents.consent_definitions]
            )
            self.raise_validation_error(
                {
                    fldname: _(
                        "Date does not fall within a valid consent period. "
                        "Possible consents are '%(possible_consents)s'. "
                        % {"possible_consents": possible_consents}
                    )
                },
                error_code,
            )
        return consent_definition
