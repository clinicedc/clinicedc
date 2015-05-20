from django import forms

from edc.base.form.forms import BaseModelForm
from edc.core.bhp_common.utils import convert_from_camel
from edc.data_manager.models import TimePointStatus

from edc_consent import AttachedModel


class BaseConsentedModelForm(BaseModelForm):

    """Base Form for all models that confirm a valid subject edc_consent to be
    available before allowing data collection.

    That is the "model" must be backed by a edc_consent."""

    def __init__(self, *args, **kwargs):
        self.check_attached()
        super(BaseConsentedModelForm, self).__init__(*args, **kwargs)

    def check_attached(self):
        """Confirms only that model exists in AttachedModel of the Consent Catalogue.

        This does not filter by consent_version, because we don't know it here, which
        means you may not get the result you expect. For example, if a model is to be
        added/changed under version 1 but is listed for both version 1 and version 2
        where v1 is inactive and v2 is active, an error will NOT be raised here since
        the query will True for the version 2 model."""
        if (not AttachedModel.objects.filter(
                content_type_map__model=self._meta.model._meta.object_name.lower(), is_active=True).exists()):
            raise AttributeError('Models registered to BaseConsentModelForm must be listed, and active, '
                                 'in AttachedModel of the ConsentCatalogue. Model {0} not found or '
                                 'not active.'.format(self._meta.model._meta.object_name.lower()))

    def clean(self):
        """Checks if subject has a valid edc_consent for this subject model
        instance and versioned fields."""
        cleaned_data = self.cleaned_data
        try:
            appointment = cleaned_data.get(
                convert_from_camel(self.visit_model()._meta.object_name)).appointment
        except AttributeError:
            appointment = cleaned_data.get('appointment')
        TimePointStatus.check_time_point_status(
            appointment,
            exception_cls=forms.ValidationError)
        # get the helper class
        consent_helper_cls = self._meta.model().get_consent_helper_cls()
        # check if consented to complete this form
        consent_helper_cls((self._meta.model, cleaned_data), forms.ValidationError).is_consented_for_subject_instance()
        # Validates fields under edc_consent version control and other checks.
        consent_helper_cls((self._meta.model, cleaned_data), forms.ValidationError).validate_versioned_fields()
        # validate that the off study form has not been entered with an off
        # study date less that or equal to report_datetime
        consent_helper_cls((self._meta.model, cleaned_data), forms.ValidationError).is_off_study()
        return super(BaseConsentedModelForm, self).clean()
