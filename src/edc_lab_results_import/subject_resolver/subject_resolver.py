from __future__ import annotations

from collections import Counter

from edc_registration import get_registered_subject_model_cls
from edc_screening.utils import get_subject_screening_model_cls

from ..constants import (
    SUBJECT_NOT_FOUND,
    VALID_SCREENING_IDENTIFER,
    VALID_SUBJECT_IDENTIFER,
)
from .subject_resolution import SubjectResolution


class SubjectResolver:
    def __init__(self):
        self.known_identifiers_cache = self.get_known_identifiers()
        self.category_cache: dict[str, tuple[str, str]] = {}
        self.reasons: Counter = Counter()
        self.unresolved_count = 0
        self.subject_not_found_count = 0

        self.match_category: str = ""
        self.match_comment: str = ""

    def resolve(
        self, *, name_id: str, subject_identifier: str, screening_identifier: str
    ) -> SubjectResolution:
        if name_id in self.known_identifiers_cache:  # check as is
            subject_resolution = self.known_identifiers_cache[name_id]
            if subject_resolution.subject_identifier:
                self.category_cache[name_id] = VALID_SUBJECT_IDENTIFER, ""
            elif subject_resolution.screening_identifier:
                self.category_cache[name_id] = VALID_SCREENING_IDENTIFER, ""
            else:
                raise ValueError()
        elif subject_identifier in self.known_identifiers_cache:
            subject_resolution = self.known_identifiers_cache[subject_identifier]
            self.known_identifiers_cache[name_id] = subject_resolution
            self.category_cache[name_id] = VALID_SUBJECT_IDENTIFER, ""
        elif screening_identifier in self.known_identifiers_cache:
            subject_resolution = self.known_identifiers_cache[screening_identifier]
            self.known_identifiers_cache[name_id] = subject_resolution
            self.category_cache[name_id] = VALID_SCREENING_IDENTIFER, ""
        else:
            subject_resolution = SubjectResolution()
            self.category_cache[name_id] = SUBJECT_NOT_FOUND, "unknown identifier"
            self.subject_not_found_count += 1

        if not subject_resolution.resolved:
            self.unresolved_count += 1
            subject_resolution.match_category, subject_resolution.match_comment = (
                self.category_cache[name_id]
            )
            self.reasons[subject_resolution.match_comment] += 1
        return subject_resolution

    @staticmethod
    def get_known_identifiers() -> dict[str, SubjectResolution]:
        subject_identifiers = get_registered_subject_model_cls().objects.values_list(
            "subject_identifier", flat=True
        )
        identifiers = {
            identifier: SubjectResolution(subject_identifier=identifier, resolved=True)
            for identifier in set(subject_identifiers)
            if identifier
        }

        screening_identifiers = get_subject_screening_model_cls().objects.values_list(
            "screening_identifier", flat=True
        )
        identifiers.update(
            {
                identifier: SubjectResolution(screening_identifier=identifier, resolved=True)
                for identifier in set(screening_identifiers)
                if identifier
            }
        )
        return identifiers
