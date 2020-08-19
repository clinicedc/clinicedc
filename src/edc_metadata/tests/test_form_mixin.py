from django.test.client import RequestFactory
from edc_metadata.form_validators.metadata_form_validator_mixin import (
    MetaDataFormValidatorMixin,
)
from edc_form_validators.form_validator import FormValidator

from .test_view_mixin import TestViewMixin, MyView


class MyForm(MetaDataFormValidatorMixin, FormValidator):

    pass


class TestForm(TestViewMixin):
    def test_(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request)
        view.appointment = self.appointment
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)
        form = MyForm(cleaned_data={}, instance=view.appointment)
        self.assertTrue(form.crf_metadata_exists)
        self.assertTrue(form.crf_metadata_required_exists)
        self.assertTrue(form.requisition_metadata_exists)
        self.assertTrue(form.requisition_metadata_required_exists)
        form.validate()
