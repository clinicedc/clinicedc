from django.apps import apps as django_apps

from edc_registration.models import RegisteredSubject

from .base_label import BaseLabel, app_config, edc_protocol_app_config


class AliquotLabel(BaseLabel):

    template_name = 'aliquot'
    model = django_apps.get_model(*app_config.aliquot_model.split('.'))
    requisition_model = django_apps.get_model(
        *app_config.requisition_model.split('.'))

    def __init__(self, pk=None, children_count=None):
        super().__init__(pk=pk)
        self._registered_subject = None
        self._requisition = None
        self.children_count = children_count
        self.aliquot = self.object

    @property
    def label_name(self):
        return self.object.human_readable_identifier

    @property
    def requisition(self):
        if not self._requisition:
            self._requisition = self.requisition_model.objects.get(
                requisition_identifier=self.object.requisition_identifier)
        return self._requisition

    @property
    def registered_subject(self):
        if not self._registered_subject:
            self._registered_subject = RegisteredSubject.objects.get(
                subject_identifier=self.object.subject_identifier)
        return self._registered_subject

    @property
    def context(self):
        return {
            'aliquot_identifier': self.aliquot.human_readable_identifier,
            'aliquot_count': 1 if self.aliquot.is_primary else self.aliquot.count,
            'children_count': 1 if self.aliquot.is_primary else self.children_count,
            'primary': '<P>' if self.aliquot.is_primary else '',
            'barcode_value': self.aliquot.aliquot_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': self.requisition.study_site,
            'clinician_initials': self.requisition.user_created[0:2].upper(),
            'drawn_datetime': self.requisition.drawn_datetime.strftime(
                '%Y-%m-%d %H:%M'),
            'subject_identifier': self.aliquot.subject_identifier,
            'gender': self.registered_subject.gender,
            'dob': self.registered_subject.dob,
            'initials': self.registered_subject.initials,
            'alpha_code': self.aliquot.alpha_code}
