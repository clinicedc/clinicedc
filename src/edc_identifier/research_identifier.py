from copy import copy
from string import Formatter

from django.apps import apps as django_apps

from .checkdigit_mixins import LuhnMixin
from .exceptions import ResearchIdentifierError
from .models import IdentifierModel

edc_device_app_config = django_apps.get_app_config('edc_device')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class ResearchIdentifier(LuhnMixin):

    label = None  # e.g. subject_identifier, plot_identifier, etc
    exception = ResearchIdentifierError

    def __init__(self, object_to_identify=None, requesting_model=None,
                 template=None, identifier=None, **kwargs):
        # e.g. 'subject', 'infant', 'plot', a.k.a subject_type
        self.object_to_identify = object_to_identify
        self.requesting_model = requesting_model
        self.template = template or self.template
        kwargs.update(
            device_id=kwargs.get('device_id', edc_device_app_config.device_id),
            protocol_number=kwargs.get(
                'protocol_number', edc_protocol_app_config.protocol_number))
        self.template_options = copy(kwargs)
        if identifier:
            # load an existing identifier
            self.identifier_model = IdentifierModel.objects.get(
                identifier=identifier)
            self.identifier = self.identifier_model.identifier
            self.subject_type = self.identifier_model.subject_type
            self.study_site = self.identifier_model.study_site
        else:
            if not self.missing_args:
                self.create(**kwargs)

    def create(self, **kwargs):
        """Creates a new and unique identifier and updates
        the IdentifierModel.
        """
        self.template_options.update(
            sequence=str(self.sequence_number).rjust(self.padding, '0'))
        identifier = self.template.format(**self.template_options)
        self.identifier = '{}-{}'.format(
            identifier, self.calculate_checkdigit(''.join(identifier.split('-'))))
        self.identifier_model = IdentifierModel.objects.create(
            name=self.label,
            sequence_number=self.sequence_number,
            identifier=self.identifier,
            protocol_number=self.template_options.get('protocol_number'),
            device_id=self.template_options.get('device_id'),
            model=self.requesting_model,
            study_site=self.template_options.get('study_site'),
            subject_type=self.object_to_identify)

    def __str__(self):
        return self.identifier

    @property
    def padding(self):
        return 5

    @property
    def missing_args(self):
        """Raises an exception if an arg used in the template is
        not provided.
        """
        formatter = Formatter()
        template_options = copy(self.template_options)
        template_options.update(sequence='0000')
        fields = [tpl[1] for tpl in formatter.parse(self.template)]
        for field in fields:
            try:
                if not template_options[field]:
                    raise self.exception(
                        'Required option not provided. Got {}'.format(field))
            except KeyError:
                raise self.exception(
                    'Required option not provided. Got {}'.format(field))

    @property
    def sequence_number(self):
        """Returns the next sequence number to use.
        """
        try:
            identifier_model = IdentifierModel.objects.filter(
                name=self.label,
                device_id=self.template_options.get('device_id'),
                study_site=self.template_options.get(
                    'study_site')).order_by('-sequence_number').first()
            sequence_number = identifier_model.sequence_number + 1
        except AttributeError:
            sequence_number = 1
        return sequence_number
