from django.contrib import admin
from django.urls.conf import path
from django.conf import settings

from .views import PrintRequisitionLabelsView, VerifyRequisitionLabelView, PrintClinicManifestView

app_name = 'edc_subject_dashboard'

urlpatterns = [
    path(r'print_requisition_labels/',
         PrintRequisitionLabelsView.as_view(),
         name='print_requisition_labels_url'),
    path(r'verify_requisition_label/',
         VerifyRequisitionLabelView.as_view(),
         name='verify_requisition_label_url'),
    path(r'print_clinic_manifest/',
         PrintClinicManifestView.as_view(),
         name='print_clinic_manifest_url'),
]

if settings.APP_NAME == 'edc_subject_dashboard':

    from edc_appointment.admin_site import edc_appointment_admin
    from edc_subject_dashboard.tests.admin import edc_subject_dashboard_admin
    urlpatterns += [
        path('admin/', admin.site.urls),
        path('admin/', edc_subject_dashboard_admin.urls),
        path('admin/', edc_appointment_admin.urls),
    ]
