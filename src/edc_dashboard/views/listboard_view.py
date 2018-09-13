import six

from django.apps import apps as django_apps
from django.views.generic.list import ListView
from edc_base.sites import SiteQuerysetViewMixin

from ..view_mixins import UrlRequestContextMixin, TemplateRequestContextMixin
from ..view_mixins import QueryStringViewMixin, SearchListboardMixin


class ListboardViewError(Exception):
    pass


class Base(QueryStringViewMixin, UrlRequestContextMixin,
           SearchListboardMixin,
           TemplateRequestContextMixin, ListView):

    cleaned_search_term = None
    context_object_name = 'results'
    empty_queryset_message = 'Nothing to display.'
    listboard_template = None  # an existing key in request.context_data
    permissions_warning_message = 'You do not have permission to view these data.'

    # if self.listboard_url declared through another mixin.
    listboard_url = None  # an existing key in request.context_data

    # default, info, success, danger, warning, etc. See Bootstrap.
    listboard_panel_style = 'default'
    listboard_fa_icon = "fas fa-user-circle"
    listboard_model = None  # label_lower model name or model class
    listboard_panel_title = None
    listboard_view_permission_codename = None
    listboard_view_only_my_permission_codename = None

    model_wrapper_cls = None
    ordering = '-created'

    orphans = 3
    paginate_by = 10
    paginator_url = None  # defaults to listboard_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context.get(self.context_object_name)
        context_object_name = self.get_context_object_name(queryset)
        wrapped_queryset = self.get_wrapped_queryset(queryset)
        if self.listboard_fa_icon and self.listboard_fa_icon.startswith('fa-'):
            self.listboard_fa_icon = f'fa {self.listboard_fa_icon}'
        context.update(
            empty_queryset_message=self.empty_queryset_message,
            has_listboard_model_perms=self.has_listboard_model_perms,
            has_view_listboard_perms=self.has_view_listboard_perms,
            listboard_fa_icon=self.listboard_fa_icon,
            listboard_panel_style=self.listboard_panel_style,
            listboard_panel_title=self.listboard_panel_title,
            listboard_view_permission_codename=self.listboard_view_permission_codename,
            object_list=wrapped_queryset,
            permissions_warning_message=self.permissions_warning_message,
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

    @property
    def has_view_listboard_perms(self):
        """Returns True if request.user has permissions to
        view the listboard.

        If False, `get_queryset` returns an empty queryset.
        """
        return self.request.user.has_perms([self.listboard_view_permission_codename])

    @property
    def has_view_only_my_listboard_perms(self):
        """Returns True if request.user only has permissions to
        view my records on the listboard.
        """
        return self.request.user.has_perm(
            self.listboard_view_only_my_permission_codename)

    @property
    def has_listboard_model_perms(self):
        """Returns True if request.user has permissions to
        add/change the listboard model.

        Does not affect `get_queryset`.

        Used in templates.
        """
        app_label = (
            self.listboard_model_cls._meta.label_lower.split('.')[0])
        model_name = (
            self.listboard_model_cls._meta.label_lower.split('.')[1])
        return self.request.user.has_perms(
            f'{app_label}.add_{model_name}',
            f'{app_label}.change_{model_name}')

    def get_template_names(self):
        return [self.get_template_from_context(self.listboard_template)]

    @property
    def url_kwargs(self):
        """Returns a dictionary of URL options for either the
        Search form URL and the Form Action.
        """
        return {}

    @property
    def listboard_model_cls(self):
        """Returns the listboard's model class.

        Accepts `listboard_model` as a model class or label_lower.
        """
        if not self.listboard_model:
            raise ListboardViewError(
                f'Listboard model not declared. Got None. See {repr(self)}')
        try:
            return django_apps.get_model(self.listboard_model)
        except (ValueError, AttributeError):
            return self.listboard_model

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

    def get_filtered_queryset(self, filter_options=None, exclude_options=None):
        """Returns a queryset, called by `get_queryset`.

        This can be overridden but be sure to use the default_manager.
        """
        return self.listboard_model_cls.objects.filter(
            **filter_options).exclude(**exclude_options)

    def get_queryset(self):
        """Return the queryset for this view.

        Completely overrides ListView.get_queryset.

        Only returns records if user has dashboard permissions to
        do so. See `has_view_listboard_perms`.

        Passes filter/exclude criteria to `get_filtered_queryset`.

        Note: The returned queryset is set to self.object_list in
        `get()` just before rendering to response.
        """
        queryset = self.listboard_model_cls._default_manager.none()
        if self.has_view_listboard_perms:
            filter_options = self.get_queryset_filter_options(
                self.request, *self.args, **self.kwargs)
            if self.has_view_only_my_listboard_perms:
                filter_options.update(
                    user_created=self.request.user.username)
            exclude_options = self.get_queryset_exclude_options(
                self.request, *self.args, **self.kwargs)
            queryset = self.get_filtered_queryset(
                filter_options=filter_options,
                exclude_options=exclude_options)
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, six.string_types):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        return queryset

    def get_wrapped_queryset(self, queryset):
        """Returns a list of wrapped model instances.

        Usually is passed the queryset `object_list` and wraps each
        instance just before passing to the template.
        """
        wrapped_objs = []
        for obj in queryset:
            model_wrapper = self.model_wrapper_cls(obj)
            model_wrapper = self.update_wrapped_instance(
                model_wrapper)
            wrapped_objs.append(model_wrapper)
        return wrapped_objs

    def update_wrapped_instance(self, model_wrapper):
        return model_wrapper


class ListboardView(SiteQuerysetViewMixin, Base):
    pass
