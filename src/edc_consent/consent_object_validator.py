from django.apps import apps as django_apps
from django.conf import settings
from edc_utils import convert_php_dateformat

from .exceptions import ConsentVersionSequenceError


class ConsentPeriodError(Exception):
    pass


class ConsentPeriodOverlapError(Exception):
    pass


class ConsentObjectValidator:
    def __init__(self, consent=None, consents=None):
        self.consents = consents
        self.check_consent_period_within_study_period(consent)
        self.check_consent_period_for_overlap(consent)
        self.check_version(consent)
        self.check_updates_versions(consent)

    def get_consents_by_model(self, model=None):
        """Returns a list of consents configured with the given
        consent model label_lower.
        """
        return [consent for consent in self.consents if consent.model == model]

    def get_consents_by_version(self, model=None, version=None):
        """Returns a list of consents of "version" configured with
        the given consent model.
        """
        consents = self.get_consents_by_model(model=model)
        return [consent for consent in consents if consent.version == version]

    def check_consent_period_for_overlap(self, new_consent=None):
        """Raises an error if consent period overlaps with an
        already registered consent object.
        """
        for consent in self.consents:
            if consent.model == new_consent.model:
                if (
                    new_consent.start <= consent.start <= new_consent.end
                    or new_consent.start <= consent.end <= new_consent.end
                ):
                    raise ConsentPeriodOverlapError(
                        f"Consent period overlaps with an already registered consent."
                        f"See alrwady registered consent {consent}. "
                        f"Got {new_consent}."
                    )

    def check_consent_period_within_study_period(self, new_consent=None):
        """Raises if the start or end date of the consent period
        it not within the opening and closing dates of the protocol.
        """
        edc_protocol_app_config = django_apps.get_app_config("edc_protocol")
        study_open_datetime = edc_protocol_app_config.study_open_datetime
        study_close_datetime = edc_protocol_app_config.study_close_datetime
        for index, dt in enumerate([new_consent.start, new_consent.end]):
            if not (study_open_datetime <= dt <= study_close_datetime):
                dt_label = "start" if index == 0 else "end"
                formatted_study_open_datetime = study_open_datetime.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                formatted_study_close_datetime = study_close_datetime.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                formatted_dt = dt.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise ConsentPeriodError(
                    f"Invalid consent. Consent period for {new_consent.name} "
                    "must be within study opening/closing dates of "
                    f"{formatted_study_open_datetime} - "
                    f"{formatted_study_close_datetime}. "
                    f"Got {dt_label}={formatted_dt}."
                )

    def check_updates_versions(self, new_consent=None):
        for version in new_consent.updates_versions:
            if not self.get_consents_by_version(
                model=new_consent.model, version=version
            ):
                raise ConsentVersionSequenceError(
                    f"Consent version {version} cannot be an update to version(s) "
                    f"'{new_consent.updates_versions}'. "
                    f"Version '{version}' not found for '{new_consent.model}'"
                )

    def check_version(self, new_consent=None):
        if self.get_consents_by_version(
            model=new_consent.model, version=new_consent.version
        ):
            raise ConsentVersionSequenceError(
                "Consent version already registered. "
                f"Version {new_consent.version}. "
                f"Got {new_consent}."
            )
