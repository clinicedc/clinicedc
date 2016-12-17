from copy import copy
from string import Formatter

from django.apps import apps as django_apps

from edc_protocol.mixins import SubjectTypeCapMixin

from .exceptions import SubjectIdentifierError
from .models import IdentifierModel
from .research_identifier import ResearchIdentifier

edc_device_app_config = django_apps.get_app_config('edc_device')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class SubjectIdentifier(SubjectTypeCapMixin, ResearchIdentifier):

    template = '{protocol_number}-{study_site}{device_id}{sequence}'
    label = 'subjectidentifier'
    exception = SubjectIdentifierError

    def __init__(self, subject_type_name=None, model=None, template=None, identifier=None,
                 create_registration=None, **kwargs):
        self.create_registration = create_registration
        super(SubjectIdentifier, self).__init__(
            object_to_identify=subject_type_name, requesting_model=model, template=template, identifier=identifier, **kwargs)

    def create(self, **kwargs):
        super(SubjectIdentifier, self).create(**kwargs)
        if self.create_registration:
            RegisteredSubject = django_apps.get_app_config('edc_registration').model
            field_names = [field.name for field in RegisteredSubject._meta.get_fields()]
            kwargs.update(subject_identifier=self.identifier)
            kwargs.update(subject_type=self.object_to_identify)
            copy_of_kwargs = copy(kwargs)
            for key in copy_of_kwargs:
                if key not in field_names:
                    del kwargs[key]
            RegisteredSubject.objects.create(**kwargs)

    @property
    def padding(self):
        return len(str(self.cap.max_subjects))

    @property
    def cap(self):
        identifier_model = IdentifierModel.objects.filter(
            name=self.label,
            subject_type=self.object_to_identify,
            model=self.requesting_model)
        self.fetch_or_raise_on_cap_met(
            subject_type_name=self.object_to_identify,
            model=self.requesting_model,
            count=identifier_model.count())
        cap = self.get_cap(
            subject_type_name=self.object_to_identify,
            model=self.requesting_model,
            study_site=self.template_options.get('study_site'))
        return cap
