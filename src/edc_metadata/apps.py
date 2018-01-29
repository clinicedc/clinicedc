import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT

from .constants import REQUISITION, CRF


style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_metadata'
    verbose_name = 'Edc Metadata'
    app_label = 'edc_metadata'
    crf_model_name = 'crfmetadata'
    requisition_model_name = 'requisitionmetadata'

    reason_field = {'edc_metadata.subjectvisit': 'reason'}
    create_on_reasons = [SCHEDULED, UNSCHEDULED]
    delete_on_reasons = [MISSED_VISIT]

    def ready(self):
        from .signals import (
            metadata_update_on_post_save,
            metadata_create_on_post_save,
            metadata_reset_on_post_delete,
        )

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        if self.app_label == self.name:
            sys.stdout.write(
                f' * using default metadata models from \'{self.app_label}\'\n')
        else:
            sys.stdout.write(
                f' * using custom metadata models from \'{self.app_label}\'\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def crf_model(self):
        """Returns the meta data model used by Crfs.
        """
        return django_apps.get_model(self.app_label, self.crf_model_name)

    @property
    def requisition_model(self):
        """Returns the meta data model used by Requisitions.
        """
        return django_apps.get_model(self.app_label, self.requisition_model_name)

    def get_metadata_model(self, category):
        if category == CRF:
            return self.crf_model
        elif category == REQUISITION:
            return self.requisition_model
        return None

    def get_metadata(self, subject_identifier, **options):
        return {
            CRF: self.crf_model.objects.filter(
                subject_identifier=subject_identifier, **options),
            REQUISITION: self.requisition_model.objects.filter(
                subject_identifier=subject_identifier, **options)}


if settings.APP_NAME == 'edc_metadata':

    from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
    from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            'edc_metadata': ('subject_visit', 'edc_metadata.subjectvisit')}

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            '7-day-clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                                 slots=[100, 100, 100, 100, 100, 100, 100]),
            '5-day-clinic': dict(days=[MO, TU, WE, TH, FR],
                                 slots=[100, 100, 100, 100, 100])}
