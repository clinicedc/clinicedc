from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin


class BoxItemView(EdcBaseViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab/home.html'
    navbar_name = 'specimens'
    box_model = django_apps.get_app_config('edc_lab').box_model
    box_item_model = django_apps.get_app_config('edc_lab').box_item_model
    add = False
    delete = False
    box_identifier = None
    box_item_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def model(self):
        return django_apps.get_model(*self.box_item_model.split('.'))

    @property
    def box_model_class(self):
        return django_apps.get_model(*self.box_model.split('.'))

    def post(self, request, *args, **kwargs):
        self.box_item_identifier = request.POST.get('box_item_identifier')
        self.box_identifier = ''.join(
            escape(request.POST.get('box_identifier')).strip().split('-'))
        if request.POST.get('box_item_action') == 'Add':
            self.add_box_item(request)
        url = reverse(
            django_apps.get_app_config('edc_lab').box_listboard_url_name,
            kwargs={'box_identifier': self.box_identifier})
        return HttpResponseRedirect(url)

    def add_box_item(self, request, **kwargs):
        if self.box_item_identifier:
            box_item_identifier = ''.join(
                escape(self.box_item_identifier).strip().split('-'))
            try:
                obj = self.model.objects.get(
                    box__box_identifier=self.box_identifier,
                    identifier=box_item_identifier)
            except self.model.DoesNotExist:
                box = self.box_model_class.objects.get(
                    box_identifier=self.box_identifier)
                obj = self.model(
                    box=box,
                    identifier=box_item_identifier,
                    position=box.next_position)
                obj.save()
            else:
                message = 'Duplicate item. {} is already in position {}.'.format(
                    self.box_item_identifier, obj.position)
                messages.error(request, message)
