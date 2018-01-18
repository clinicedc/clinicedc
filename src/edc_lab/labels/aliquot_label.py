from django.apps import apps as django_apps

from edc_registration.models import RegisteredSubject

from .base_label import BaseLabel


edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class AliquotLabel(BaseLabel):

    model_attr = 'aliquot_model'
    template_name = 'aliquot'

    def __init__(self, pk=None, children_count=None, request=None):
        super().__init__(pk=pk, request=request)
        self._registered_subject = None
        self._requisition = None
        self.children_count = children_count
        self.aliquot = self.object

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
                subject_identifier=self.requisition.subject_identifier)
        return self._registered_subject

    @property
    def label_context(self):
        return {
            'aliquot_identifier': self.aliquot.human_readable_identifier,
            'aliquot_count': 1 if self.aliquot.is_primary else self.aliquot.count,
            'children_count': 1 if self.aliquot.is_primary else self.children_count,
            'primary': '<P>' if self.aliquot.is_primary else '',
            'barcode_value': self.aliquot.aliquot_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': str(self.requisition.site.id),
            'site_name': str(self.requisition.site.name),
            'clinician_initials': self.requisition.user_created[0:2].upper(),
            'drawn_datetime': self.requisition.drawn_datetime.strftime(
                '%Y-%m-%d %H:%M'),
            'subject_identifier': self.registered_subject.subject_identifier,
            'gender': self.registered_subject.gender,
            'dob': self.registered_subject.dob,
            'initials': self.registered_subject.initials,
            'alpha_code': self.aliquot.alpha_code,
            'panel': self.requisition.panel_object.abbreviation}
