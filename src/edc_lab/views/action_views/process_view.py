import re

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import UUID_PATTERN
from edc_dashboard.view_mixins import AppConfigViewMixin

from ..mixins import ProcessViewMixin


class ProcessView(ProcessViewMixin, EdcBaseViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab/home.html'
    navbar_name = 'specimens'
    requisition_model = django_apps.get_app_config('edc_lab').requisition_model

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def model(self):
        return django_apps.get_model(*self.requisition_model.split('.'))

    def post(self, request, *args, **kwargs):
        requisitions = []
        for pk in request.POST.getlist('requisitions'):
            if re.match(UUID_PATTERN, pk):
                requisitions.append(pk)
        self.process(requisitions)
        url = reverse(
            django_apps.get_app_config('edc_lab').process_listboard_url_name)
        return HttpResponseRedirect(url)
