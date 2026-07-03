from unittest.mock import patch

from django.test import TestCase, override_settings, tag

from edc_identifier.checkdigit_mixins import LuhnMixin
from edc_lab_results.constants import (
    OUT_OF_SCOPE,
    REASON_BAD_CHECK_DIGIT,
    REASON_FOREIGN,
    REASON_INVALID_SCREENING,
    REASON_UNREGISTERED_SITE,
    REASON_VALID_SCREENING,
    REASON_VALID_SUBJECT,
    SUBJECT_NOT_FOUND,
)
from edc_lab_results.import_results import (
    category_for_unresolved,
    classify_identifier,
)


@tag("lab_results")
@override_settings(
    EDC_PROTOCOL_SUBJECT_IDENTIFIER_PATTERN=r"\b999-\d{2}-\d{4}-\d{1}\b",
    EDC_PROTOCOL_SCREENING_IDENTIFIER_PATTERN=r"[A-Z0-9]{8}",
)
class TestClassifyIdentifier(TestCase):
    """protocol (pattern) + registered site (edc_sites) + Luhn check digit +
    SubjectScreening membership."""

    def setUp(self):
        # site 40 registered; 77 is not.
        site_patch = patch(
            "edc_lab_results.import_results._registered_site_ids",
            return_value={40},
        )
        site_patch.start()
        self.addCleanup(site_patch.stop)
        # by default, no screening is known (screening-shaped -> invalid)
        self.screening_patch = patch(
            "edc_lab_results.import_results._screening_exists",
            return_value=False,
        )
        self.mock_screening = self.screening_patch.start()
        self.addCleanup(self.screening_patch.stop)

    @staticmethod
    def _checkdigit(body: str) -> str:
        return LuhnMixin().calculate_checkdigit(body)

    def test_valid_subject(self):
        cd = self._checkdigit("999400001")
        self.assertEqual(
            classify_identifier(f"999-40-0001-{cd}"), REASON_VALID_SUBJECT
        )

    def test_bad_check_digit(self):
        cd = self._checkdigit("999400001")
        wrong = str((int(cd) + 1) % 10)
        self.assertEqual(
            classify_identifier(f"999-40-0001-{wrong}"), REASON_BAD_CHECK_DIGIT
        )

    def test_unregistered_site(self):
        # matches the subject pattern, but site 77 is not registered
        self.assertEqual(
            classify_identifier("999-77-0001-0"), REASON_UNREGISTERED_SITE
        )

    def test_foreign_wrong_protocol(self):
        # 101 does not match the 999 pattern, and isn't 8-char screening-shaped
        self.assertEqual(classify_identifier("101-40-0001-1"), REASON_FOREIGN)

    def test_invalid_screening_when_not_in_subjectscreening(self):
        # screening-shaped, but no matching SubjectScreening -> typo
        self.assertEqual(
            classify_identifier("ABCD1234"), REASON_INVALID_SCREENING
        )

    def test_valid_screening_when_in_subjectscreening(self):
        self.mock_screening.return_value = True
        self.assertEqual(classify_identifier("ABCD1234"), REASON_VALID_SCREENING)
        self.mock_screening.assert_called_once_with("ABCD1234")

    def test_screening_dash_stripped_before_lookup(self):
        self.mock_screening.return_value = True
        self.assertEqual(classify_identifier("S228-9WY3"), REASON_VALID_SCREENING)
        self.mock_screening.assert_called_once_with("S2289WY3")

    def test_foreign_junk(self):
        self.assertEqual(classify_identifier("MHM"), REASON_FOREIGN)

    def test_category_valid_subject_is_reissueable(self):
        cd = self._checkdigit("999400001")
        category, reason = category_for_unresolved(f"AAA/999-40-0001-{cd}")
        self.assertEqual(category, SUBJECT_NOT_FOUND)
        self.assertEqual(reason, REASON_VALID_SUBJECT)

    def test_category_bad_check_digit_is_reissueable(self):
        category, _ = category_for_unresolved("AAA/999-40-0001-0")
        # 0 is (almost certainly) the wrong Luhn digit -> still reissue-able
        self.assertIn(category, {SUBJECT_NOT_FOUND})

    def test_category_invalid_screening_is_reissueable(self):
        category, reason = category_for_unresolved("AAA/ABCD1234")
        self.assertEqual(category, SUBJECT_NOT_FOUND)
        self.assertEqual(reason, REASON_INVALID_SCREENING)

    def test_category_foreign_is_out_of_scope(self):
        category, reason = category_for_unresolved("AAA/101-40-0001-1")
        self.assertEqual(category, OUT_OF_SCOPE)
        self.assertEqual(reason, REASON_FOREIGN)

    def test_category_unregistered_site_is_out_of_scope(self):
        category, reason = category_for_unresolved("AAA/999-77-0001-0")
        self.assertEqual(category, OUT_OF_SCOPE)
        self.assertEqual(reason, REASON_UNREGISTERED_SITE)
