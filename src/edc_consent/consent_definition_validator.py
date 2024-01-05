from __future__ import annotations

from typing import TYPE_CHECKING

from edc_protocol import Protocol
from edc_utils import floor_secs, formatted_datetime
from edc_utils.date import ceil_datetime, floor_datetime

from .exceptions import ConsentVersionSequenceError

if TYPE_CHECKING:
    from .consent_definition import ConsentDefinition


class ConsentPeriodError(Exception):
    pass


class ConsentPeriodOverlapError(Exception):
    pass


class ConsentDefinitionValidator:
    def __init__(
        self,
        consent_definition: ConsentDefinition = None,
        consent_definitions: list[ConsentDefinition] = None,
    ):
        self.consent_definitions = consent_definitions
        self.check_consent_period_within_study_period(consent_definition)
        self.check_consent_period_for_overlap(consent_definition)
        self.check_version(consent_definition)
        self.check_updates_versions(consent_definition)

    def get_consent_definitions_by_model(self, model: str = None) -> list[ConsentDefinition]:
        """Returns a list of ConsentDefinitions configured with the
        given consent model label_lower.
        """
        return [cdef for cdef in self.consent_definitions if cdef.model == model]

    def get_consent_definitions_by_version(
        self, model: str = None, version: str = None
    ) -> list[ConsentDefinition]:
        """Returns a list of ConsentDefinitions of "version"
        configured with the given consent model.
        """
        consents = self.get_consent_definitions_by_model(model=model)
        return [consent for consent in consents if consent.version == version]

    def check_consent_period_for_overlap(
        self, consent_definition: ConsentDefinition = None
    ) -> None:
        """Raises an error if consent period overlaps with an
        already registered consent object.
        """
        for cdef in self.consent_definitions:
            if cdef.model == consent_definition.model:
                if (
                    consent_definition.start <= cdef.start <= consent_definition.end
                    or consent_definition.start <= cdef.end <= consent_definition.end
                ):
                    raise ConsentPeriodOverlapError(
                        f"Consent period overlaps with an already registered consent."
                        f"See already registered consent {cdef}. "
                        f"Got {consent_definition}."
                    )

    @staticmethod
    def check_consent_period_within_study_period(consent_definition: ConsentDefinition = None):
        """Raises if the start or end date of the consent period
        it not within the opening and closing dates of the protocol.
        """
        protocol = Protocol()
        study_open_datetime = protocol.study_open_datetime
        study_close_datetime = protocol.study_close_datetime
        for index, dt in enumerate([consent_definition.start, consent_definition.end]):
            if not (
                floor_secs(floor_datetime(study_open_datetime))
                <= floor_secs(dt)
                <= floor_secs(ceil_datetime(study_close_datetime))
            ):
                dt_label = "start" if index == 0 else "end"
                formatted_study_open_datetime = formatted_datetime(study_open_datetime)
                formatted_study_close_datetime = formatted_datetime(study_close_datetime)
                formatted_dt = formatted_datetime(dt)
                raise ConsentPeriodError(
                    f"Invalid consent. Consent period for {consent_definition.name} "
                    "must be within study opening/closing dates of "
                    f"{formatted_study_open_datetime} - "
                    f"{formatted_study_close_datetime}. "
                    f"Got {dt_label}={formatted_dt}."
                )

    def check_updates_versions(self, consent_definition: ConsentDefinition = None):
        for version in consent_definition.updates_versions:
            if not self.get_consent_definitions_by_version(
                model=consent_definition.model, version=version
            ):
                raise ConsentVersionSequenceError(
                    f"Consent version {version} cannot be an update to version(s) "
                    f"'{consent_definition.updates_versions}'. "
                    f"Version '{version}' not found for '{consent_definition.model}'"
                )

    def check_version(self, consent_definition: ConsentDefinition = None):
        if self.get_consent_definitions_by_version(
            model=consent_definition.model, version=consent_definition.version
        ):
            raise ConsentVersionSequenceError(
                "Consent version already registered. "
                f"Version {consent_definition.version}. "
                f"Got {consent_definition}."
            )
