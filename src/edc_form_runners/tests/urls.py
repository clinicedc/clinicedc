from django.contrib import admin
from django.urls.conf import include, path
from django.views.generic import RedirectView

app_name = "edc_form_runner"


urlpatterns = []


urlpatterns += [
    path("accounts/", include("edc_auth.urls")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", RedirectView.as_view(url="/admin"), name="home_url"),
]
