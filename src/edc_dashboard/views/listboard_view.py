import six

from django.utils.html import escape
from django.apps import apps as django_apps
from django.db.models import Q
from django.utils.text import slugify
from django.views.generic.list import ListView
from edc_constants.constants import OTHER, YES, NO

from ..view_mixins import QueryStringViewMixin


class ListboardView(QueryStringViewMixin, ListView):

    model = None  # label_lower model name
    context_object_name = 'results'
    model_wrapper_cls = None
    ordering = '-created'
    pagination_limit = 10
    paginate_by = 10
    orphans = 3
    listboard_url_name = None
    cleaned_search_term = None
    page = None
    empty_queryset_message = 'Nothing to display'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_term = None

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).listboard_template_name]

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

    def pagination_limit_reached(self, context):
        """Returns a boolean that verifies if pagination limit has been reached
        """
        if context.get('paginator').num_pages > self.pagination_limit:
            return True
        else:
            return False

    def is_last_pages(self, context):
        """Returns a boolean that verifies if current page lies in the range
        of the last pages to be shown
        """
        current_page = int(self.kwargs.get('page'))
        num_pages = context.get('paginator').num_pages
        last_pages_range = range(num_pages - self.pagination_limit + 1,
                                 num_pages + 1)
        return current_page in last_pages_range

    def page_range_list(self, context):
        """Returns a list of page numbers that will be shown in the template
        """
        if self.kwargs.get('page'):
            if not self.is_last_pages(context):
                return [i for i in range(int(self.kwargs.get('page')),
                                         int(self.kwargs.get('page')) +
                                         self.pagination_limit)]
            else:
                return [i for i in range(context.get('paginator').num_pages -
                                         self.pagination_limit + 1,
                                         context.get('paginator').num_pages +
                                         1)]
        else:
            return [i for i in range(1, self.pagination_limit + 1)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context.get('object_list')  # from ListView
        context_object_name = self.get_context_object_name(queryset)
        wrapped_queryset = self.get_wrapped_queryset(queryset)
        context.update(
            OTHER=OTHER,
            YES=YES,
            NO=NO,
            empty_queryset_message=self.empty_queryset_message,
            listboard_url_name=self.listboard_url_name,
            object_list=wrapped_queryset,
            search_term=self.search_term,
            pagination_limit_reached=self.pagination_limit_reached(context),
            page_range=self.page_range_list(context))
        if context_object_name is not None:
            context[context_object_name] = wrapped_queryset
        return context
