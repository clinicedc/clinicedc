from django.contrib import admin
from django.urls import path
# from django.conf import settings
# from edc_base.views import LoginView, LogoutView

from .admin_site import edc_pharmacy_admin
# from .views import HomeView, PatientRecordView


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'admin/', edc_pharmacy_admin.urls),
    #     url(r'^edc_label/', include('edc_label.urls', namespace='edc-label')),
    #     url(r'^edc/', include('edc_base.urls', namespace='edc-base')),
    #     url(r'^(?P<page>\d+)/$', HomeView.as_view(), name='home_url'),
    #     url(r'^patient_record/(?P<subject_identifier>[-\w]+)/(?P<page>\d+)/$', PatientRecordView.as_view(), name='patient'),
    #     url(r'^dispense_print/(?P<subject_identifier>[-\w]+)/(?P<dispense_pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
    #         PatientRecordView.as_view(), name='print_url'),
    #     url(r'^patient_record/(?P<subject_identifier>[-\w]+)/$', PatientRecordView.as_view(), name='patient_url'),
    #     url(r'^', HomeView.as_view(), name='home_url'),
    #     url(r'^(?P<subject_identifier>[-\w]+)/(?P<page>\d+)/$', HomeView.as_view(), name='home_url'),
    #     url(r'^(?P<subject_identifier>[-\w]+)/$', HomeView.as_view(), name='home_url'),
]


# if settings.APP_NAME == 'edc_pharma':
#     urlpatterns += [
#         path(r'login', LoginView.as_view(), name='login_url'),
#         path(r'logout', LogoutView.as_view(
#             pattern_name='login_url'), name='logout_url'),
#     ]
