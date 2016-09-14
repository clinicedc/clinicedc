from django.conf.urls import url

from .views import SubjectDashboardView, HomeView, MostRecentView

urlpatterns = [
    # url(r'^subject/(?P<subject_identifier>.*)/$', SubjectDashboardView.as_view(), name='subject_dashboard'),
    # url(r'^(?P<subject_identifier>.*)/$', HomeView.as_view(), name='home_url'),
    url(r'^recent/(?P<model>\w+)/', MostRecentView.as_view(), name='most-recent'),
    # url(r'^', HomeView.as_view(), name='home_url'),
]
