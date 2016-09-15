import json

from crispy_forms.utils import render_crispy_form
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View

from django_paginator import PaginatorMixin
from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin

from .forms import SubjectSearchForm
from edc.subject.consent_old.classes.controller import site_consents


app_config = django_apps.get_app_config('edc_dashboard')


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_dashboard/home.html'


class MostRecentView(PaginatorMixin, View):

    paginate_by = 1
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            model = django_apps.get_model(*app_config.most_recent_models['subject'].split('.'))
            qs = model.objects.all().order_by('-created')
            json_data = self.paginate_to_json(qs, self.kwargs.get('page', 1))
            return HttpResponse(json_data, content_type='application/json')
        raise TypeError()


class SubjectSearchView(PaginatorMixin, View):

    http_method_names = ['get', 'post']

    def get_success_url(self):
        return reverse('home_url')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Renders the form, validates, and looks for a matching model instance."""
        if request.is_ajax():
            data = {}
            form_context = {}
            form = SubjectSearchForm(request.POST or None)
            if form.is_valid():
                model, attr = app_config.search_models.get('subject')
                model = django_apps.get_model(*model.split('.'))
                try:
                    qs = model.objects.filter(**{attr + '__startswith': form.cleaned_data['search_term']})
                    if not qs:
                        raise model.DoesNotExist()
                    form_context.update({'object': qs[0]})
                    data.update(self.paginate_as_dict(qs, 1))
                except model.DoesNotExist:
                    form.add_error('search_term', 'Not found. Got \'{}\''.format(form.cleaned_data['search_term']))
            form_context.update(csrf(request))
            form_html = render_crispy_form(form, context=form_context)
            data.update({'form_html': form_html})
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponseRedirect(reverse(self.get_success_url()))


class QueryModelView(PaginatorMixin, View):

    paginate_by = 10

    http_method_names = ['get', 'post']

    @property
    def queryset(self):
        if self.kwargs['lookup_name'] == 'consent':
            consent_config = site_consents.get_by_subject_type(self.kwargs['subject_type'])
            model = consent_config.model
            lookup = {'subject_identifier': self.kwargs['subject_type']}
            ordering = 'version'
        return model.objects.filter(**lookup).order_by(ordering)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            json_data = self.paginate_to_json(self.queryset, self.kwargs.get('page', 1))
            return HttpResponse(json_data, content_type='application/json')
        raise TypeError()

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
