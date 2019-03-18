import os

from django.conf import settings
from django.views.generic import ListView, TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.views import DashboardView as BaseDashboardView

from .models import CrfOne


class HomeView(TemplateView):
    template_name = os.path.join(
        settings.BASE_DIR, "edc_model_admin", "tests", "templates", "home.html"
    )


class DashboardView(EdcViewMixin, BaseDashboardView):

    dashboard_url = "subject_dashboard_url"
    dashboard_template = "subject_dashboard_template"


#     def get_context_data(self, **kwargs):
#         context_data = super().get_context_data(**kwargs)
#         context_data.update({"project_name": "project_name"})
#         return context_data


class CrfOneListView(ListView):
    model = CrfOne
    fields = ["subject_identifier", "subject_visit"]
    template_name = os.path.join(
        settings.BASE_DIR, "edc_model_admin", "tests", "templates", "crfmodel_list.html"
    )
