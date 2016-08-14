from django.conf.urls import url

from edc_dashboard.views import SubjectDashboardView, HomeView

urlpatterns = [
    url(r'^subject/(?P<subject_identifier>.*)/$', SubjectDashboardView.as_view(), name='subject_dashboard'),
    url(r'^', HomeView.as_view(), name='home_url'),
]
