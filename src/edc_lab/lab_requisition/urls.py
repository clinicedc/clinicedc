from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^requisition/(?P<subject_type>\w+)/(?P<requisition_identifier_label>requisition_identifier)/(?P<identifier>\w+)/$',
        'view_requisition',
        name="view_requisition"),
   url(r'^requisition/(?P<subject_type>\w+)/(?P<requisition_identifier_label>specimen_identifier)/(?P<identifier>\w+)/$',
        'view_requisition',
        name="view_requisition"))
