from django.db import models
from django.apps import apps as django_apps

from edc_identifier.old_identifier import Identifier


class AliquotManager(models.Manager):

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)


class DestinationManager(models.Manager):

    def get_by_natural_key(self, code):
        return self.get(code=code)


class PackingListManager(models.Manager):

    def get_by_natural_key(self, timestamp):
        return self.get(timestamp=timestamp)


class PackingListItemManager(models.Manager):

    def get_by_natural_key(self, item_reference):
        return self.get(item_reference=item_reference)


class SpecimenCollectionManager(models.Manager):

    def get_by_natural_key(self, collection_identifier):
        return self.get(collection_identifier=collection_identifier)


class SpecimenCollectionItemManager(models.Manager):

    def get_by_natural_key(self, specimen_identifier):
        return self.get(specimen_identifier=specimen_identifier)


class ReceiveManager(models.Manager):

    def get_by_natural_key(self, receive_identifier):
        return self.get(receive_identifier=receive_identifier)


class RequisitionManager(models.Manager):

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)

    def get_global_identifier(self, **kwargs):
        """Generates and returns a globally unique requisition identifier
        (adds site and protocolnumber)"""
        edc_device_app_config = django_apps.get_app_config('edc_device')
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
        if not edc_device_app_config.is_server:
            raise ValueError(
                'Only SERVERs may access method \'get_global_identifier\' machine_type.')
        identifier = Identifier(
            subject_type='specimen',
            site_code=kwargs.get('site_code', 'SITE??'),  # TODO: site_code: where does this come from?
            protocol_code=kwargs.get('protocol_code', edc_protocol_app_config.protocol),
            counter_length=4)
        identifier.create()

        return identifier
