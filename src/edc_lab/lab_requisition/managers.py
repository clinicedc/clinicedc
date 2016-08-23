from django.apps import apps as django_apps
from django.db import models

from edc_identifier.old_identifier import Identifier


class RequisitionManager(models.Manager):

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)

    def get_global_identifier(self, **kwargs):
        """Generates and returns a globally unique requisition identifier
        (adds site and protocolnumber)"""
        edc_device_app_config = django_apps.get_app_config('edc_device')
        if not edc_device_app_config.is_server:
            raise ValueError(
                'Only SERVERs may access method \'get_global_identifier\' machine_type.')
        identifier = Identifier(
            subject_type='specimen',
            site_code=kwargs.get('site_code', settings.SITE_CODE),
            protocol_code=kwargs.get('protocol_code', settings.PROTOCOL_NUMBER),
            counter_length=4)
        identifier.create()

        return identifier
