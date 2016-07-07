from django.apps import AppConfig
from django.apps import apps as django_apps


class EdcAppointmentAppConfig(AppConfig):
    name = 'edc_appointment'
    verbose_name = "Appointments"
    model = ('example', 'appointment')
    appointments_days_forward = 0
    appointments_per_day_max = 30
    use_same_weekday = True
    allowed_iso_weekdays = '1234567'
    default_appt_type = 'clinic'

    @property
    def appointment_model(self):
        return django_apps.get_model(*self.model)

    def ready(self):
        import edc_appointment.signals


# count = 0
# for sl in SubjectLocator.objects.filter(may_contact_someone='No', has_alt_contact='No'):
#     sl.has_alt_contact = 'N/A'
#     sl.modified = datetime.today()
#     sl.user_modified = 'ckgathi'
#     print sl.registered_subject.subject_identifier
#     try:
#         sl.save()
#     except ValidationError:
#         pass
#     except EnrollmentChecklist.DoesNotExist:
#         pass
#     except NameError:
#         pass
#     count += 1
#     print count
# count = 0
# for sl in SubjectLocator.objects.filter(may_contact_someone='No', has_alt_contact='Yes'):
#     sl.contact_name = sl.alt_contact_name
#     sl.contact_rel = sl.alt_contact_rel
#     sl.contact_cell = sl.alt_contact_cell
#     sl.alt_contact_cell_number = sl.other_alt_contact_cell
#     sl.contact_phone = sl.alt_contact_tel
#     sl.modified = datetime.today()
#     sl.user_modified = 'ckgathi'
#     sl.save()
#     count += 1
#     print count
#     
#     
# consents = SubjectConsent.objects.filter(version='?')
# count = 0
# total = consents.count()
# print("Updating {} consents where version == \'?\'  ".format(total))
# for consent in consents:
#     try:
#         consent.save()
#         count += 1
#         print ("{0} done out of {1}".format(count, total))
#         print("Done.")
#     except ValidationError:
#         pass
#     except EnrollmentChecklist.DoesNotExist:
#         pass
#     except MultipleObjectsReturned:
#         pass
