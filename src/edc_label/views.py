from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_label.label import Label
from edc_label.view_mixins import EdcLabelViewMixin


class HomeView(EdcBaseViewMixin, EdcLabelViewMixin, TemplateView):

    template_name = 'edc_label/home.html'

#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(HomeView, self).dispatch(*args, **kwargs)


class ModelPrint(HomeView):

    @property
    def model(self):
        return django_apps.get_model(self.kwargs.get('app_label'), self.kwargs.get('model_name'))

    def get_object(self):
        try:
            obj = self.model.get(pk=self.kwargs.get('pk'))
        except self.model.DoesNotExist:
            obj = None
        return obj

    @property
    def object(self):
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = super(ModelPrint, self).get_context_data(**kwargs)
        try:
            label_context = self.object.to_label_context()
        except AttributeError:
            label_context = self.object.__dict__
        label = Label(label_context, self.kwargs.get('label_name'))
        label.print_label(self.kwargs.get('copies'), 1)
        context.update({
            'label_message': label.message,
            'label_error_message': label.error_message,
        })
        return context
