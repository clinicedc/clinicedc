from edc_lab.models import BoxItem

from ...view_mixins import BoxViewMixin
from .base_listboard_view import BaseListboardView


class BaseBoxItemListboardView(BoxViewMixin, BaseListboardView):

    navbar_selected_item = 'pack'
    ordering = ('-position', )
    listboard_model = BoxItem

    def get_queryset_filter_options(self, request, *args, **kwargs):
        return {'box': self.box}
