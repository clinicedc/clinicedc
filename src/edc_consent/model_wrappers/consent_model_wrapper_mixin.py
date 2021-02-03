from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_identifier import is_subject_identifier_or_raise
from edc_model_wrapper import ModelWrapper
from edc_utils import get_uuid

from ..site_consents import site_consents


class ConsentModelWrapperMixin(ModelWrapper):

    consent_model_wrapper_cls = None

    @property
    def consent_object(self):
        """Returns a consent configuration object from site_consents
        relative to the wrapper's "object" report_datetime.
        """
        default_consent_group = django_apps.get_app_config("edc_consent").default_consent_group
        consent_object = site_consents.get_consent_for_period(
            model=self.consent_model_wrapper_cls.model,
            report_datetime=self.object.report_datetime,
            consent_group=default_consent_group,
        )
        return consent_object

    @property
    def consent_model_obj(self):
        """Returns a consent model instance or None."""
        consent_model_cls = django_apps.get_model(self.consent_model_wrapper_cls.model)
        try:
            model_obj = consent_model_cls.objects.get(**self.consent_options)
        except ObjectDoesNotExist:
            model_obj = None
        return model_obj

    @property
    def consent(self):
        """Returns a wrapped saved or unsaved consent."""
        model_obj = self.consent_model_obj or self.consent_object.model_cls(
            **self.create_consent_options
        )
        return self.consent_model_wrapper_cls(model_obj=model_obj)

    @property
    def create_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_object.version,
        )
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            subject_identifier=is_subject_identifier_or_raise(
                self.object.subject_identifier, reference_obj=self.object
            ),
            version=self.consent_object.version,
        )
        return options
