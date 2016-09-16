from django.conf.urls import url

from .views import MostRecentView, SubjectSearchView, QueryModelView

urlpatterns = [
    url(r'^recent/(?P<model>[\w]+)/(?P<page>[\d]+)/', MostRecentView.as_view(), name='most-recent'),
    url(r'^recent/(?P<model>[\w]+)/', MostRecentView.as_view(), name='most-recent'),
    url(r'^search/subject/', SubjectSearchView.as_view(), name='subject-search'),
    url(r'^query/(?P<lookup_name>[\w]+)/(?P<subject_type>[\w]+)/(?P<subject_identifier>[\w]+)/', QueryModelView.as_view(), name='query-model'),
]
