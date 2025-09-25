from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, tag

from edc_constants.constants import OTHER
from edc_metadata.tests.tests.metadata_test_mixin import TestMetadataMixin
from edc_transfer.form_validators import SubjectTransferFormValidator
from edc_transfer.forms import SubjectTransferForm

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


@tag("transfer")
@override_settings(SITE_ID=10)
class TestTransfer(TestMetadataMixin, TestCase):
    def test_form_ok(self):
        data = dict(subject_identifier=self.appointment.subject_identifier)
        form = SubjectTransferForm(data=data)
        form.is_valid()

    def test_form_validator(self):
        data = dict(subject_identifier=self.appointment.subject_identifier, initiated_by=OTHER)
        form = SubjectTransferFormValidator(cleaned_data=data)
        self.assertRaises(ValidationError, form.validate)

        data.update(initiated_by_other="blah")
        form = SubjectTransferFormValidator(cleaned_data=data)

        try:
            form.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")
