import json

from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_device/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        app_config = django_apps.get_app_config('edc_device')
        context.update({
            'project_name': '{}: {}'.format(context.get('project_name'), app_config.verbose_name),
            'app_config': app_config,
        })
        return context

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(HomeView, self).dispatch(*args, **kwargs)
