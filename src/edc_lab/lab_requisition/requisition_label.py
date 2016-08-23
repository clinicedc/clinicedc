from django.conf import settings

from edc_registration.models import RegisteredSubject


class RequisitionLabel:

    def refresh_label_context(self):
        requisition = self.model_instance
        subject_identifier = requisition.get_subject_identifier()
        registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_identifier)
        may_store_samples = registered_subject.may_store_samples
        custom = {}
        custom.update({
            'aliquot_count': 1,
            'aliquot_type': requisition.aliquot_type.alpha_code.upper(),
            'barcode_value': requisition.barcode_value(),
            'clinician_initials': requisition.user_created[0:2].upper(),
            'dob': registered_subject.dob,
            'drawn_datetime': requisition.drawn_datetime,
            'gender': registered_subject.gender,
            'initials': registered_subject.initials,
            'item_count_total': requisition.item_count_total,
            'may_store_samples': may_store_samples,
            'panel': requisition.panel.name[0:21],
            'protocol': settings.PROTOCOL_NUMBER,
            'requisition_identifier': requisition.requisition_identifier,
            'site': requisition.study_site,
            'specimen_identifier': requisition.specimen_identifier,
            'subject_identifier': subject_identifier,
            'visit': requisition.get_visit().appointment.visit_definition.code,
        })
        try:
            custom.update({'hiv_status_code': str(requisition.hiv_status_code()), })
        except AttributeError:
            pass
        try:
            custom.update({'art_status_code': str(requisition.art_status_code()), })
        except AttributeError:
            pass
        self.label_context.update(**custom)

    def print_label_for_requisition(self, request, requisition):
        """ Prints a requisition label."""
        if requisition.requisition_identifier:
            self.print_label(request, requisition, 1)
