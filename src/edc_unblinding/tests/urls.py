from django.urls.conf import path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(), name="home_url"),
]
