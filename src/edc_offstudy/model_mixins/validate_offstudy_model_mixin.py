from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from edc_constants.date_constants import EDC_DATETIME_FORMAT


class ValidateOffstudyError(Exception):
    pass


class ValidateOffstudyModelMixin:

    @property
    def consented_before_offstudy(self):
        consent = None
        try:
            model_cls = django_apps.get_model(self._meta.consent_model)
        except AttributeError as e:
            raise ValidateOffstudyError(
                f'Failed to lookup consent model. Meta class option '
                f'consent_model={self._meta.consent_model} for model {repr(self)}. '
                f'Got {e}')
        try:
            consent = model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                consent_datetime__lte=self.offstudy_datetime)
        except ObjectDoesNotExist:
            consent = None
        return consent

    def offstudy_datetime_after_last_visit_or_raise(self, visit_model_cls=None):
        last_visit = visit_model_cls.objects.filter(
            subject_identifier=self.subject_identifier).order_by(
                'report_datetime').last()
        if last_visit and (last_visit.report_datetime - self.offstudy_datetime).days > 0:
            formatted_visitdate = timezone.localtime(
                last_visit.report_datetime).strftime(EDC_DATETIME_FORMAT)
            formatted_offstudy = timezone.localtime(
                self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
            raise ValidateOffstudyError(
                f'Offstudy datetime cannot precede the last visit date of '
                f'{formatted_visitdate}. Got Offstudy date {formatted_offstudy}')

    class Meta:
        abstract = True
