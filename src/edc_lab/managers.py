from django.db import models
# from django.apps import apps as django_apps

# from edc_identifier.old_identifier import Identifier


class AliquotManager(models.Manager):

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)


class ManifestManager(models.Manager):

    def get_by_natural_key(self, manifest_identifier):
        return self.get(manifest_identifier=manifest_identifier)


class RequisitionManager(models.Manager):

    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)

#     def get_global_identifier(self, **kwargs):
#         """Generates and returns a globally unique requisition identifier
#         (adds site and protocolnumber)"""
#         edc_device_app_config = django_apps.get_app_config('edc_device')
#         edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
#         if not edc_device_app_config.is_server:
#             raise ValueError(
#                 'Only SERVERs may access method \'get_global_identifier\' machine_type.')
#         identifier = Identifier(
#             subject_type='specimen',
#             # TODO: site_code: where does this come from?
#             site_code=kwargs.get('site_code', 'SITE??'),
#             protocol_code=kwargs.get(
#                 'protocol_code', edc_protocol_app_config.protocol),
#             counter_length=4)
#         identifier.create()
#
#         return identifier
