from django.conf import settings

from edc_registration.models import RegisteredSubject

from lis.labeling.classes import ModelLabel
from lis.labeling.models import ZplTemplate


class RequisitionLabel(ModelLabel):

    def __init__(self):
        super(RequisitionLabel, self).__init__()
        template_name = 'requisition_label'
        if not ZplTemplate.objects.filter(name=template_name):
            template_string = (
                '^XA\n'
                '^FO325,5^A0N,15,20^FD%(protocol)s Site %(site)s %(label_count)s/%(label_count_total)s^FS\n'
                '^FO320,20^BY1,3.0^BCN,50,N,N,N\n'
                '^BY^FD%(specimen_identifier)s^FS\n'
                '^FO320,80^A0N,15,20^FD%(specimen_identifier)s [%(requisition_identifier)s]^FS\n'
                '^FO325,100^A0N,15,20^FD%(panel)s %(aliquot_type)s^FS\n'
                '^FO325,118^A0N,16,20^FD%(subject_identifier)s (%(initials)s)^FS\n'
                '^FO325,136^A0N,16,20^FDDOB: %(dob)s %(gender)s^FS\n'
                '^FO325,152^A0N,20^FD%(drawn_datetime)s^FS\n'
                '^XZ')
            self.zpl_template = ZplTemplate.objects.create(
                name=template_name,
                template=template_string)
        else:
            self.zpl_template = ZplTemplate.objects.get(name=template_name)

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
