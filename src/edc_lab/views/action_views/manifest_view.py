from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.utils.decorators import method_decorator

from ..mixins import ManifestViewMixin
from .base_action_view import BaseActionView, app_config


class ManifestView(ManifestViewMixin, BaseActionView):

    post_url_name = app_config.manifest_listboard_url_name
    valid_form_actions = [
        'remove_selected_items']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'remove_selected_items':
            self.remove_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items, if allowed.
        """
        if not self.selected_items:
            message = ('Nothing to do. No manifests have been selected.')
            messages.warning(self.request, message)
        else:
            try:
                deleted = self.manifest_model.objects.filter(
                    pk__in=self.selected_items).delete()
                message = (
                    '{} manifest(s) have been removed.'.format(deleted[0]))
                messages.success(self.request, message)
            except ProtectedError:
                message = ('Unable to remove. Manifest is not empty.')
                messages.error(self.request, message)
