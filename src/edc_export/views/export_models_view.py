from typing import Any

from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..exportables import Exportables


class ExportModelsView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_export/export_models.html"
    navbar_name = "edc_export"
    navbar_selected_item = "export"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        if self.kwargs.get("action") == "cancel":
            try:
                self.request.session.pop("selected_models")
            except KeyError:
                pass
            else:
                messages.info(self.request, "Nothing has been exported.")
        user = User.objects.get(username=self.request.user)
        kwargs.update(exportables=Exportables(request=self.request, user=user))
        return super().get_context_data(**kwargs)
