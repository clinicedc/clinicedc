from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin


class HomeView(EdcViewMixin, TemplateView):

    template_name = f"edc_metadata/bootstrap{settings.EDC_BOOTSTRAP}/home.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
