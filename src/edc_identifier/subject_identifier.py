from copy import copy
from string import Formatter

from django.apps import apps as django_apps

from edc_protocol.mixins import SubjectTypeCapMixin

from .checkdigit_mixins import LuhnMixin
from .exceptions import SubjectIdentifierError
from .models import IdentifierModel

edc_device_app_config = django_apps.get_app_config('edc_device')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class SubjectIdentifier(LuhnMixin, SubjectTypeCapMixin):

    def __init__(self, subject_type_name, model, template=None, **template_options):
        self.template = template or '{protocol_number}-{study_site}{device_id}{sequence}'
        self.template_options = template_options
        self.template_options.update(
            device_id=self.template_options.get('device_id', edc_device_app_config.device_id),
            protocol_number=self.template_options.get('protocol_number', edc_protocol_app_config.protocol_number))
        if not self.missing_args:
            identifier_model = IdentifierModel.objects.filter(
                name='subjectidentifier',
                subject_type=subject_type_name,
                model=model)
            self.fetch_or_raise_on_cap_met(
                subject_type_name=subject_type_name,
                model=model,
                count=identifier_model.count())
            cap = self.get_cap(
                subject_type_name=subject_type_name,
                model=model,
                study_site=self.template_options.get('study_site'))
            padding = len(str(cap.max_subjects))
            self.template_options.update(
                sequence=str(self.sequence_number).rjust(padding, '0'))
            identifier = self.template.format(**self.template_options)
            self.identifier = '{}-{}'.format(
                identifier, self.calculate_checkdigit(''.join(identifier.split('-'))))
            IdentifierModel.objects.create(
                name=self.name,
                sequence_number=self.sequence_number,
                identifier=self.identifier,
                protocol_number=self.template_options.get('protocol_number'),
                device_id=self.template_options.get('device_id'),
                model=model,
                study_site=self.template_options.get('study_site'),
                subject_type=subject_type_name)

    def __str__(self):
        return self.identifier

    @property
    def name(self):
        return 'subjectidentifier'

    @property
    def missing_args(self):
        """Raises an exception if an arg used in the template is not provided."""
        formatter = Formatter()
        template_options = copy(self.template_options)
        template_options.update(sequence='0000')
        fields = [tpl[1] for tpl in formatter.parse(self.template)]
        for field in fields:
            try:
                if not template_options[field]:
                    raise SubjectIdentifierError('Required option not provided. Got {}'.format(field))
            except KeyError:
                raise SubjectIdentifierError('Required option not provided. Got {}'.format(field))

    @property
    def sequence_number(self):
        """Returns the next sequence number to use."""
        try:
            identifier_model = IdentifierModel.objects.filter(
                name='subjectidentifier',
                device_id=self.template_options.get('device_id'),
                study_site=self.template_options.get('study_site')).order_by('-sequence_number').first()
            sequence_number = identifier_model.sequence_number + 1
        except AttributeError:
            sequence_number = 1
        return sequence_number
