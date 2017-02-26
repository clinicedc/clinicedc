from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView, app_config
from django.db.models.deletion import ProtectedError


class PackView(BoxViewMixin, BaseActionView):

    post_url_name = app_config.pack_listboard_url_name
    box_item_failed = False
    valid_form_actions = [
        'remove_selected_items']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'remove_selected_items':
            self.remove_selected_items()

    def remove_selected_items(self):
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.box_model.objects.filter(
                    pk__in=self.selected_items).delete()
                message = ('{} items have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Box is not empty.')
                messages.error(self.request, message)
