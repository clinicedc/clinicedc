from django.urls.conf import path

from .admin_site import edc_lab_results_import_admin
from .views import ResultSearchView, SourceDocumentView
from .views.home_view import HomeView

app_name = "edc_lab_results_import"


urlpatterns = [
    path("admin/", edc_lab_results_import_admin.urls),
    path("result-search/", ResultSearchView.as_view(), name="result_search_url"),
    path(
        "source-document/<uuid:pk>/",
        SourceDocumentView.as_view(),
        name="source_document_url",
    ),
    # path("", RedirectView.as_view(url="/edc_lab_results_import/admin/"), name="home_url"),
    path("", HomeView.as_view(), name="home_url"),
]
