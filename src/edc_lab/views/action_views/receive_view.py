import re

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.utils import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import UUID_PATTERN, YES
from edc_dashboard.view_mixins import AppConfigViewMixin

from ...specimen import Specimen
from ..mixins import ProcessViewMixin


class ReceiveView(ProcessViewMixin, EdcBaseViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab/home.html'
    navbar_name = 'specimens'
    requisition_model = django_apps.get_app_config('edc_lab').requisition_model
    receive_and_process = False

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
        if request.POST.get('receive'):
            self.receive(requisitions)
            self.create_specimens(requisitions)
        elif request.POST.get('receive_and_process'):
            self.receive(requisitions)
            self.create_specimens(requisitions)
            self.process(requisitions)
        url = reverse(
            django_apps.get_app_config('edc_lab').receive_listboard_url_name)
        return HttpResponseRedirect(url)

    def receive(self, requisitions=None):
        return self.model.objects.filter(
            pk__in=requisitions, is_drawn=YES).exclude(
                received=True).update(
                    received=True, received_datetime=get_utcnow())

    def create_specimens(self, requisitions=None):
        for requisition in self.model.objects.filter(
                pk__in=requisitions, received=True):
            Specimen(requisition=requisition)
