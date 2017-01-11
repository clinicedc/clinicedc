from django.core.paginator import Paginator, EmptyPage


class PaginatorMixin:

    paginate_by = 10

    def paginate(self, queryset=None, model_wrapper_class=None):
        """Paginates a queryset."""
        paginator = Paginator(queryset, self.paginate_by)
        try:
            page = paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        page = self.page_object_list_wrapper(
            page=page, model_wrapper_class=model_wrapper_class)
        return page

    def page_object_list_wrapper(self, page=None, model_wrapper_class=None):
        """Wraps the filtered queryset objects."""
        object_list = []
        qs = page.object_list
        for obj in qs:
            object_list.append(model_wrapper_class(obj))
        page.object_list = object_list
        return page
