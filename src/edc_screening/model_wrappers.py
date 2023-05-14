from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_consent import ConsentModelWrapperMixin
from edc_dashboard.utils import get_dashboard_app_label
from edc_model_wrapper import ModelWrapper
from edc_refusal.model_wrappers import SubjectRefusalModelWrapper
from edc_subject_model_wrappers import SubjectConsentModelWrapper as BaseModelWrapper
from edc_subject_model_wrappers import SubjectRefusalModelWrapperMixin

from edc_screening.utils import get_subject_screening_model


class SubjectConsentModelWrapper(BaseModelWrapper):
    @property
    def querystring(self):
        return (
            f"cancel={get_dashboard_app_label()}:screening_listboard_url,"
            f"screening_identifier&{super().querystring}"
        )


class SubjectScreeningModelWrapper(
    SubjectRefusalModelWrapperMixin, ConsentModelWrapperMixin, ModelWrapper
):
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    refusal_model_wrapper_cls = SubjectRefusalModelWrapper
    model = get_subject_screening_model()
    next_url_attrs = ["screening_identifier"]
    next_url_name = "screening_listboard_url"
    querystring_attrs = ["gender"]

    @property
    def create_consent_options(self):
        options = super().create_consent_options
        options.update(screening_identifier=self.object.screening_identifier)
        return options

    @property
    def consent_options(self):
        return dict(screening_identifier=self.object.screening_identifier)

    @property
    def eligible(self) -> bool:
        return self.object.eligible

    @property
    def consent_model_obj(self):
        consent_model_cls = django_apps.get_model(self.consent_model_wrapper_cls.model)
        try:
            return consent_model_cls.objects.get(**self.consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def human_screening_identifier(self):
        human = None
        if self.screening_identifier:
            human = f"{self.screening_identifier[0:4]}-{self.screening_identifier[4:]}"
        return human or self.screening_identifier
