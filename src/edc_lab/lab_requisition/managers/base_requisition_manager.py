from django.db import models
from edc.core.bhp_variables.models import StudySpecific
from edc.core.identifier.classes import Identifier


class BaseRequisitionManager(models.Manager):
    def get_by_natural_key(self, requisition_identifier):
        return self.get(requisition_identifier=requisition_identifier)

    def get_global_identifier(self, **kwargs):

        """Generates and returns a globally unique requisition identifier (adds site and protocolnumber)"""

        if not StudySpecific.objects.all()[0].machine_type == 'SERVER':
            raise ValueError('Only SERVERs may access method \'get_global_identifier\'. \
                              Machine Type is determined from model StudySpecific attribute \
                              machine_type. Got %s' % (StudySpecific.objects.all()[0].machine_type,))
        site_code = kwargs.get('site_code')
        protocol_code = kwargs.get('protocol_code', '')
        if not site_code:
            try:
                site_code = StudySpecific.objects.all()[0].site_code
            except AttributeError:
                raise AttributeError('Requisition needs a \'site_code\'. Got None. Either pass as a parameter or in StudySpecific')
        if len(site_code) == 1:
            site_code = site_code + '0'
        if not protocol_code:
            try:
                protocol_code = StudySpecific.objects.all()[0].protocol_code
            except AttributeError:
                raise AttributeError('Requisition needs a \'protocol_code\'. Got None. Either pass as a parameter or set in StudySpecific')
        identifier = Identifier(subject_type='specimen',
                                site_code=site_code,
                                protocol_code=protocol_code,
                                counter_length=4,
                                )
        identifier.create()

        return identifier
