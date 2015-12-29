from django.conf.urls import patterns, url
from .views import view_lab_result, update_result_status

urlpatterns = patterns('',
    url(r'^viewresult/(?P<result_identifier>[0-9\-]+)/$',
        'view_result',
        name="view_result_report"
        ),
    url(r'^lab/result/report/view/(?P<result_identifier>[0-9\-]+)/$', view_lab_result, name='view_lab_result'),
    url(r'^lab/result/update/view/(?P<subject_identifier>[0-9\-]+)/$', update_result_status, name='update_result_status'),
)
