# from django.contrib import admin
# from django.urls import include, path
# from django.views.generic.base import RedirectView
# from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns
#
# from model_admin_app.views import CrfOneListView
#
# app_name = "model_admin_app"
#
# urlpatterns = []
#
# for app_name in [
#     "edc_dashboard",
#     "edc_auth",
#     "edc_export",
#     "edc_consent",
#     "edc_device",
#     "edc_protocol",
#     "edc_reference",
#     "edc_visit_schedule",
# ]:
#     for p in paths_for_urlpatterns(app_name):
#         urlpatterns.append(p)
#
# urlpatterns += [
#     path("admin/", admin.site.urls),
#     path("i18n/", include("django.conf.urls.i18n")),
#     path("", CrfOneListView.as_view(), name="crfone-list"),
#     path("", include("edc_model_admin.tests.dashboard_app.urls")),
#     path("", include("edc_model_admin.tests.dashboard2_app.urls")),
#     path("", RedirectView.as_view(url="admin/"), name="administration_url"),
#     path("", RedirectView.as_view(url="admin/"), name="home_url"),
#     path("", RedirectView.as_view(url="admin/"), name="logout"),
# ]
