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
    # app_label = 'edc_metadata'
    crf_model = 'edc_metadata.crfmetadata'
    metadata_requisition_model = 'edc_metadata.requisitionmetadata'
    has_exportable_data = True
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
        sys.stdout.write(
            f' * using crf metadata model \'{self.crf_model}\'\n')
        sys.stdout.write(
            f' * using requisition metadata model \'{self.metadata_requisition_model}\'\n')
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')

    @property
    def crf_model_cls(self):
        """Returns the meta data model used by Crfs.
        """
        return django_apps.get_model(self.crf_model)

    @property
    def metadata_requisition_model_cls(self):
        """Returns the meta data model used by Requisitions.
        """
        return django_apps.get_model(self.metadata_requisition_model)

    def get_metadata_model(self, category):
        if category == CRF:
            return self.crf_model_cls
        elif category == REQUISITION:
            return self.metadata_requisition_model_cls
        return None

    def get_metadata(self, subject_identifier, **options):
        return {
            CRF: self.crf_model_cls.objects.filter(
                subject_identifier=subject_identifier, **options),
            REQUISITION: self.metadata_requisition_model_cls.objects.filter(
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
