from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ..exportables import Exportables


class HomeView(EdcBaseViewMixin, NavbarViewMixin, TemplateView):

    template_name = f'edc_export/bootstrap{settings.EDC_BOOTSTRAP}/home.html'
    navbar_name = 'edc_export'
    navbar_selected_item = 'export'

    def get_context_data(self, **kwargs):
        if self.kwargs.get('action') == 'cancel':
            try:
                self.request.session.pop('selected_models')
            except KeyError:
                pass
            else:
                messages.info(
                    self.request, (f'Nothing has been exported.'))
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        context.update(exportables=Exportables(
            request=self.request, user=user))
        return context
