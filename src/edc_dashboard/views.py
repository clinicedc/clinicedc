import json

from crispy_forms.utils import render_crispy_form
from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from django.template.context_processors import csrf
from .forms import SubjectSearchForm
from django.urls.base import reverse


app_config = django_apps.get_app_config('edc_dashboard')


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_dashboard/home.html'


class PaginatorMixin:

    paginate_by = 10

    def paginate_queryset(self, qs, page_number):
        """Returns a Paginator page object given a queryset and page number."""
        paginator = Paginator(qs, self.paginate_by)
        try:
            page = paginator.page(page_number)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return page

    def paginate_as_dict(self, qs, page_number):
        page = self.paginate_queryset(qs, page_number)
        data = {}
        page_data = {k: v for k, v in page.paginator.__dict__.items() if k != 'object_list'}
        page_data.update({'number': page.number})
        data.update({'paginator': json.dumps(page_data)})
        data.update({'object_list': serializers.serialize('json', page.object_list)})
        return data

    def paginate_to_json(self, qs, page_number):
        """Returns a json object containing two serialized objects, the paginator and object_list.

        Note: In the .js, use JSON.parse for each object, for example:

            var object_list = JSON.parse( data.object_list );
            var paginator = JSON.parse( data.paginator );

        """
        return json.dumps(self.paginate_as_dict(qs, page_number))


class MostRecentView(PaginatorMixin, View):

    paginate_by = 1

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

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

    def get_success_url(self):
        return reverse('home_url')

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

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
