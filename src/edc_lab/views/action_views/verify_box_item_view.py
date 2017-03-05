from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.utils import get_utcnow

from ...exceptions import SpecimenError
from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView, app_config
from edc_lab.constants import SHIPPED


class VerifyBoxItemView(BoxViewMixin, BaseActionView):

    post_url_name = app_config.verify_box_listboard_url_name
    box_item_failed = False
    valid_form_actions = [
        'verify_item', 'reset_box', 'verify_box']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.kwargs.get('action_name'),
            'box_identifier': self.box_identifier,
            'position': self.kwargs.get('position', '1')}

    def process_form_action(self):
        if self.action == 'verify_item':
            try:
                if self.box_item_identifier:
                    self.verify_item()
            except SpecimenError:
                pass
        elif self.action == 'reset_box':
            self.unverify_box()
        elif self.action == 'verify_box':
            self.verify_box()

    def next_position(self):
        """Returns the next position relative to that from the URL.
        """
        self.kwargs['position'] = str(
            int(self.kwargs.get('position', '1')) + 1)

    def verify_item(self):
        """Updates the box_item as verified if the identifier matches
        the identifier already in that position.
        """
        if self.box.status == SHIPPED:
            message = ('Unable to verify. Box has already been shipped.')
            messages.error(self.request, message)
        else:
            box_item_in_position = self.get_box_item(
                position=self.kwargs.get('position'))
            self.redirect_querystring.update(alert=1)
            if box_item_in_position:
                if self.box_item:
                    if self.box_item == box_item_in_position:
                        box_item_in_position.verified = 1
                        box_item_in_position.verified_datetime = get_utcnow()
                        self.next_position()
                        self.redirect_querystring.pop('alert')
                    else:
                        box_item_in_position.verified = -1
                        box_item_in_position.verified_datetime = None
                else:
                    box_item_in_position.verified = 0
                    box_item_in_position.verified_datetime = None
                box_item_in_position.save()
                self.box.save()

    def unverify_box(self):
        if self.box.status == SHIPPED:
            message = ('Unable to reset. Box has already been shipped.')
            messages.error(self.request, message)
        else:
            self.box.unverify_box()
