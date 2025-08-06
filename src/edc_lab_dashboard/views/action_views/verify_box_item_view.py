from django.contrib import messages
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab import SHIPPED
from edc_utils import get_utcnow

from ...view_mixins import BoxViewMixin
from .action_view import ActionView


class VerifyBoxItemView(EdcViewMixin, BoxViewMixin, ActionView):
    post_action_url = "verify_box_listboard_url"
    box_item_failed = False
    valid_form_actions = ["verify_item", "reset_box", "verify_box"]

    @property
    def url_kwargs(self):
        return {
            "action_name": self.kwargs.get("action_name"),
            "box_identifier": self.box_identifier,
            "position": self.kwargs.get("position", "1"),
        }

    def process_form_action(self, request=None):
        if self.action == "verify_item":
            if self.box_item_identifier:
                self.verify_item()
        elif self.action == "reset_box":
            self.unverify_box()
        elif self.action == "verify_box":
            self.verify_box()

    def next_position(self):
        """Returns the next position relative to that from the URL."""
        self.kwargs["position"] = str(int(self.kwargs.get("position", "1")) + 1)

    def verify_item(self):
        """Updates the box_item as verified if the identifier matches
        the identifier already in that position.
        """
        if self.box.status == SHIPPED:
            message = "Unable to verify. Box has already been shipped."
            messages.error(self.request, message)
        else:
            box_item_in_position = self.get_box_item(position=self.kwargs.get("position"))
            self.redirect_querystring.update(alert=1)
            if box_item_in_position:
                if self.box_item:
                    if self.box_item == box_item_in_position:
                        box_item_in_position.verified = 1
                        box_item_in_position.verified_datetime = get_utcnow()
                        self.next_position()
                        self.redirect_querystring.pop("alert")
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
            message = "Unable to reset. Box has already been shipped."
            messages.error(self.request, message)
        else:
            self.box.unverify_box()
