from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_dashboard/home.html'


class SubjectDashboardView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_dashboard/subject_dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SubjectDashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EdcBaseViewMixin, self).get_context_data(**kwargs)
        subject_identifier = self.kwargs.get('subject_identifier')
        appointment = self.kwargs.get('appointment')
        visit = self.kwargs.get('visit')
        try:
            metadata = visit.metadata
        except AttributeError:
            metadata = None
        context.update({
            'subject_identifier': self.kwargs.get('subject_identifier'),
            'demographics': self.demographics(subject_identifier),
            'appointments': self.appointments(subject_identifier),
            'visit': visit,
            'metadata': metadata,
        })
        return context

    @property
    def subject_identifier(self):
        return self.kwargs.get('subject_identifier')

    def demographics(self):
        return {'first_name': 'first_name'}

    def appointments(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.model.objects.filter(subject_identifier=self.subject_identifier).order_by('visit_code')
