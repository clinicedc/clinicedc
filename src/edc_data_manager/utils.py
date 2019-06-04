from ambition_subject.admin import PatientHistoryAdmin
from ambition_subject.admin_site import ambition_subject_admin
from ambition_subject.models import PatientHistory
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test.client import RequestFactory

admin = PatientHistoryAdmin(model=PatientHistory, admin_site=ambition_subject_admin)

rf = RequestFactory()
request = rf.request()
User = get_user_model()
request.user = User.objects.get(username="erikvw")
request.site = Site.objects.all()[0]

form = admin.add_view(
    request=request,
    extra_context={
        "subject_dashboard_url": "ambition_dashboard:subject_dashboard_url",
        "subject_identifier": "092-40990004-7",
    },
)
