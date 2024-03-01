from __future__ import annotations

from datetime import datetime

from django.utils.translation import gettext as _
from edc_form_validators import INVALID_ERROR
from edc_sites.site import sites as site_sites

from edc_consent import ConsentDefinitionDoesNotExist, site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import NotConsentedError, SiteConsentError


class ConsentDefinitionFormValidatorMixin:

    def get_consent_datetime_or_raise(
        self, report_datetime: datetime = None, fldname: str = None, error_code: str = None
    ) -> datetime:
        """Returns the consent_datetime of this subject"""
        consent_obj = self.get_consent_or_raise(
            report_datetime=report_datetime, fldname=fldname, error_code=error_code
        )
        return consent_obj.consent_datetime

    def get_consent_or_raise(
        self,
        report_datetime: datetime = None,
        fldname: str | None = None,
        error_code: str | None = None,
    ) -> datetime:
        """Returns the consent_datetime of this subject.

        Wraps func `consent_datetime_or_raise` to re-raise exceptions
        as ValidationError.
        """
        fldname = fldname or "report_datetime"
        error_code = error_code or INVALID_ERROR
        consent_definition = self.get_consent_definition(
            report_datetime=report_datetime, fldname=fldname, error_code=error_code
        )
        # use the consent_definition to get the subject consent model instance
        try:
            consent_obj = consent_definition.get_consent_for(
                subject_identifier=self.subject_identifier,
                report_datetime=report_datetime,
            )
        except NotConsentedError as e:
            self.raise_validation_error({fldname: str(e)}, error_code)
        return consent_obj

    def get_consent_definition(
        self, report_datetime: datetime = None, fldname: str = None, error_code: str = None
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
