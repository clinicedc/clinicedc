from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.utils import get_utcnow

from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView, app_config


class VerifyBoxItemView(BoxViewMixin, BaseActionView):

    listboard_url_name = app_config.verify_box_listboard_url_name
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
            self.verify_item()
        elif self.action == 'reset_box':
            self.unverify_box()
        elif self.action == 'verify_box':
            self.verify_box()

    def next_position(self):
        self.kwargs['position'] = str(
            int(self.kwargs.get('position', '1')) + 1)

    def verify_item(self):
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

    def unverify_box(self):
        self.box.unverify_box()
