from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter


class OrderHasRequisitionListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Has Requisition')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'requisition'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('YES', _('Yes')),
            ('NO', _('No')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        return []
