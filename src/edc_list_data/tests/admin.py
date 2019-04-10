from django.contrib.admin import AdminSite as DjangoAdminSite

from .models import Antibiotic, Neurological, Symptom, SignificantNewDiagnosis


class AdminSite(DjangoAdminSite):
    pass


edc_list_data_admin = AdminSite(name="edc_list_data_admin")

edc_list_data_admin.register(Antibiotic)
edc_list_data_admin.register(Neurological)
edc_list_data_admin.register(Symptom)
edc_list_data_admin.register(SignificantNewDiagnosis)
