from django.apps import apps as django_apps

edc_pharma_app_config = django_apps.get_app_config('edc_pharma')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class DispenseLabelContext:
    """Format dispense record into printable ZPL label context."""

    def __init__(self, prescriptions=None, user=None):
        self.prescriptions = prescriptions
        self.user = user

    def context(self, prescription=None):
        # FIXME, request for print label from the ambition team.
        subject_identifier = prescription.subject_identifier
        category = prescription.category
        result = prescription.recommanded_result if (
            prescription.recommanded_result) else prescription.result
        return {
            'barcode_value': subject_identifier,
            'site': edc_pharma_app_config.site_code,
            'telephone_number': None,
            'medication': prescription.description,
            'clinician_initials': prescription.clinician_initials,
            'number_of_tablets': None,
            'times_per_day': None,
            'total_number_of_tablets': f'{result} {category}',
            'storage_instructions': None,
            'prepared_datetime': prescription.modified.strftime(
                '%Y-%m-%d'),
            'subject_identifier': subject_identifier,
            'prepared_by': prescription.user_modified,
            'protocol': edc_protocol_app_config.protocol,
            'initials': prescription.initials,
        }

    @property
    def context_list(self):
        context_list = []
        for prescription in self.prescriptions:
            context = self.context(prescription=prescription)
            context_list.append(context)
        return context_list
