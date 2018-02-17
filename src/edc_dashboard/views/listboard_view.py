import six

from django.utils.html import escape
from django.apps import apps as django_apps
from django.db.models import Q
from django.utils.text import slugify
from django.views.generic.list import ListView
from edc_base.sites import SiteQuerysetViewMixin
from edc_dashboard.view_mixins import UrlRequestContextMixin, TemplateRequestContextMixin

from ..view_mixins import QueryStringViewMixin


class ListboardViewError(Exception):
    pass


class Base(QueryStringViewMixin, UrlRequestContextMixin,
           TemplateRequestContextMixin, ListView):

    cleaned_search_term = None
    context_object_name = 'results'
    empty_queryset_message = 'Nothing to display'
    listboard_template = None  # an existing key in request.context_data
    listboard_url = None  # an existing key in request.context_data

    # default, info, success, danger, warning, etc. See Bootstrap.
    listboard_panel_style = 'default'
    listboard_fa_icon = "far fa-user-circle"

    model = None  # label_lower model name
    model_wrapper_cls = None
    ordering = '-created'

    orphans = 3
    paginate_by = 10
    paginator_url = None  # defaults to listboard_url

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_term = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context.get('object_list')  # from ListView
        context_object_name = self.get_context_object_name(queryset)
        wrapped_queryset = self.get_wrapped_queryset(queryset)
        if self.listboard_fa_icon and self.listboard_fa_icon.startswith('fa-'):
            self.listboard_fa_icon = f'fa {self.listboard_fa_icon}'
        context.update(
            listboard_panel_style=self.listboard_panel_style,
            listboard_fa_icon=self.listboard_fa_icon,
            empty_queryset_message=self.empty_queryset_message,
            object_list=wrapped_queryset,
            search_term=self.search_term)
        if context_object_name is not None:
            context[context_object_name] = wrapped_queryset
        context = self.add_url_to_context(
            new_key='listboard_url',
            existing_key=self.listboard_url,
            context=context)
        context = self.add_url_to_context(
            new_key='paginator_url',
            existing_key=self.paginator_url or self.listboard_url,
            context=context)
        return context

    def get_template_names(self):
        return [self.get_template_from_context(self.listboard_template)]

    @property
    def url_kwargs(self):
        """Returns a dictionary of URL options for either the
        Search form URL and the Form Action.
        """
        return {}

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        """Returns exclude options applied to every
        queryset.
        """
        return {}

    def get_queryset_filter_options(self, request, *args, **kwargs):
        """Returns filter options applied to every
        queryset.
        """
        return {}

    def extra_search_options(self, search_term):
        """Returns a search Q object that will be added to the
        search criteria (OR) for the search queryset.
        """
        return Q()

    def clean_search_term(self, search_term):
        return search_term

    @property
    def search_term(self):
        if not self._search_term:
            search_term = self.request.GET.get('q')
            if search_term:
                search_term = escape(search_term).strip()
            search_term = self.clean_search_term(search_term)
            self._search_term = search_term
        return self._search_term

    def get_queryset(self):
        """Return the list of items for this view.

        Completely overrides ListView.get_queryset.

        The return value gets set to self.object_list in get()
        just before rendering to response.
        """
        filter_options = self.get_queryset_filter_options(
            self.request, *self.args, **self.kwargs)
        exclude_options = self.get_queryset_exclude_options(
            self.request, *self.args, **self.kwargs)
        if self.search_term and '|' not in self.search_term:
            search_terms = self.search_term.split('+')
            q = None
            q_objects = []
            for search_term in search_terms:
                q_objects.append(Q(slug__icontains=slugify(search_term)))
                q_objects.append(self.extra_search_options(search_term))
            for q_object in q_objects:
                if q:
                    q = q | q_object
                else:
                    q = q_object
            queryset = self.model_cls.objects.filter(
                q or Q(), **filter_options).exclude(**exclude_options)
        else:
            queryset = self.model_cls.objects.filter(
                **filter_options).exclude(
                    **exclude_options)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_wrapped_queryset(self, queryset):
        """Returns a list of wrapped model instances.
        """
        object_list = []
        for obj in queryset:
            object_list.append(self.model_wrapper_cls(obj))
        return object_list


class ListboardView(SiteQuerysetViewMixin, Base):
    pass
