from edc.core.bhp_variables.models import StudySpecific
from edc.subject.registration.models import RegisteredSubject

from lis.labeling.classes import ModelLabel
from lis.labeling.models import ZplTemplate


class RequisitionLabel(ModelLabel):

    def __init__(self):
        super(RequisitionLabel, self).__init__()
        template_name = 'requisition_label'
        if not ZplTemplate.objects.filter(name=template_name):
            template_string = ('^XA\n'
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
        if registered_subject.may_store_samples.lower() == 'Yes':
            may_store_samples = 'Y'
        elif registered_subject.may_store_samples.lower() == 'No':
            may_store_samples = 'N'
        else:
            may_store_samples = '?'
        try:
            study_specific = StudySpecific.objects.all()[0]
        except:
            raise AttributeError('Cannot determine protocol_number. '
                                 'Please populate bhp_variables.study_specific.')
        custom = {}
        custom.update({
            'requisition_identifier': requisition.requisition_identifier,
            'barcode_value': requisition.barcode_value(),
            'specimen_identifier': requisition.specimen_identifier, })
        if 'hiv_status_code' in dir(requisition):
            custom.update({'hiv_status_code': str(requisition.hiv_status_code()), })
        if 'art_status_code' in dir(requisition):
            custom.update({'art_status_code': str(requisition.art_status_code()), })
        custom.update({
            'protocol': study_specific.protocol_number,
            'site': requisition.site.site_code,
            'panel': requisition.panel.name[0:21],
            'drawn_datetime': requisition.drawn_datetime,
            'subject_identifier': subject_identifier,
            'visit': requisition.get_visit().appointment.visit_definition.code,
            'gender': registered_subject.gender,
            'dob': registered_subject.dob,
            'initials': registered_subject.initials,
            'may_store_samples': may_store_samples,
            'aliquot_type': requisition.aliquot_type.alpha_code.upper(),
            'item_count_total': requisition.item_count_total, })
        self.label_context.update(**custom)
