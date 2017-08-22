from django.apps import apps as django_apps

from ..site_consents import site_consents
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import get_uuid


class ConsentModelWrapperMixin:

    consent_model_wrapper_cls = None

    @property
    def consent_object(self):
        """Returns a consent configuration object from site_consents
        relative to the wrapper's "object" report_datetime.
        """
        default_consent_group = django_apps.get_app_config(
            'edc_consent').default_consent_group
        consent_object = site_consents.get_consent(
            report_datetime=self.object.report_datetime,
            consent_group=default_consent_group)
        return consent_object

    @property
    def consent(self):
        """Returns a wrapped saved or unsaved consent.
        """
        try:
            consent = self.object.subjectconsent_set.get(
                **self.consent_options)
        except ObjectDoesNotExist:
            consent = self.consent_object.model(**self.create_consent_options)
        return self.consent_model_wrapper_cls(model_obj=consent)

    @property
    def create_consent_options(self):
        """Returns a dictionary of options to create a new
        consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_object.version)
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.consent_object.version)
        return options
