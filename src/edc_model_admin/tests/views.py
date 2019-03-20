import os

from django.conf import settings
from django.views.generic import ListView, TemplateView

from .models import CrfOne


class HomeView(TemplateView):
    template_name = os.path.join(
        settings.BASE_DIR, "edc_model_admin", "tests", "templates", "home.html"
    )


class CrfOneListView(ListView):
    model = CrfOne
    fields = ["subject_identifier", "subject_visit"]
    template_name = os.path.join(
        settings.BASE_DIR, "edc_model_admin", "tests", "templates", "crfmodel_list.html"
    )
