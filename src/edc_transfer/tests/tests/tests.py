from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_constants.constants import OTHER
from edc_metadata.tests.tests.metadata_test_mixin import TestMetadataMixin

from edc_transfer.form_validators import SubjectTransferFormValidator
from edc_transfer.tests.forms import SubjectTransferForm

from ..models import SubjectTransfer


class TestTransfer(TestMetadataMixin, TestCase):
    def test_ok(self):
        SubjectTransfer

    def test_form(self):
        pass

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
