import json

from django.core import serializers
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from django.http.response import HttpResponse, HttpResponseGone

app_config = django_apps.get_app_config('edc_dashboard')


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_dashboard/home.html'


class MostRecentView(View):

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            model = django_apps.get_model(*app_config.most_recent_models['subject'].split('.'))
            json_data = serializers.serialize(
                'json', model.objects.all().order_by('-created')[0:10],
                fields=('subject_identifier', 'first_name', 'initials', 'gender', 'dob', 'user_created', 'created'))
            return HttpResponse(json_data, content_type='application/json')
        return HttpResponseGone()


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
