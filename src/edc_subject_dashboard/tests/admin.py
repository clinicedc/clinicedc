from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_locator.models import SubjectLocator

from .models import Appointment, SubjectConsent, SubjectVisit


class AdminSite(DjangoAdminSite):
    pass


edc_subject_dashboard_admin = AdminSite(name="edc_subject_dashboard_admin")

edc_subject_dashboard_admin.register(Appointment)
edc_subject_dashboard_admin.register(SubjectConsent)
edc_subject_dashboard_admin.register(SubjectLocator)
edc_subject_dashboard_admin.register(SubjectVisit)
