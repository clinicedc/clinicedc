from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html
from edc_dashboard.url_names import url_names
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab import SHIPPED
from edc_lab.models import BoxIsFullError, BoxItem

from ...view_mixins import BoxViewMixin
from .action_view import ActionView


class ManageBoxItemView(EdcViewMixin, BoxViewMixin, ActionView):
    post_action_url = "manage_box_listboard_url"
    valid_form_actions = ["add_item", "renumber_items", "remove_selected_items"]

    @property
    def url_kwargs(self):
        return {
            "action_name": self.kwargs.get("action_name"),
            "box_identifier": self.box_identifier,
        }

    def process_form_action(self, request=None):
        if self.action == "add_item":
            if self.box_item_identifier:
                self.add_box_item()
        elif self.action == "renumber_items":
            self.renumber_items()
        elif self.action == "remove_selected_items":
            self.remove_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items."""
        if not self.selected_items:
            message = "Nothing to do. No items have been selected."
            messages.warning(self.request, message)
        elif self.box.status == SHIPPED:
            message = "Unable to remove. Box has already been shipped."
            messages.error(self.request, message)
        else:
            deleted = (
                BoxItem.objects.filter(pk__in=self.selected_items)
                .exclude(box__status=SHIPPED)
                .delete()
            )
            message = f"{deleted[0]} items have been removed."
            messages.success(self.request, message)

    def renumber_items(self):
        """Resets positions to be a sequence incremented by 1."""
        box_items = self.box.boxitem_set.all().order_by("position")
        if box_items.count() == 0:
            message = "Nothing to do. There are no items in the box."
            messages.warning(self.request, message)
        elif self.box.status == SHIPPED:
            message = "Unable to renumber. Box has already been shipped."
            messages.error(self.request, message)
        else:
            for index, boxitem in enumerate(
                self.box.boxitem_set.all().order_by("position"), start=1
            ):
                boxitem.position = index
                boxitem.verified = False
                boxitem.verified_datetime = None
                boxitem.save()
            self.box.save()
            message = (
                f"Box {self.box_identifier} has been renumber. "
                "Be sure to verify the position of each specimen."
            )
            messages.success(self.request, message)

    def add_box_item(self, **kwargs):  # noqa
        """Adds the item to the next available position in the box."""
        if self.box.status == SHIPPED:
            message = "Unable to add. Box has already been shipped."
            messages.error(self.request, message)
        else:
            try:
                box_item = BoxItem.objects.get(
                    box__box_identifier=self.box_identifier,
                    identifier=self.box_item_identifier,
                )
            except ObjectDoesNotExist:
                try:
                    box_item = BoxItem.objects.get(identifier=self.box_item_identifier)
                except ObjectDoesNotExist:
                    self.create_box_item()
                else:
                    message = format_html(
                        'Item is already packed. See box <a href="{}" '
                        'class="alert-link">{}</a>',
                        self.box_href,
                        box_item.box.human_readable_identifier,
                    )
                    messages.error(self.request, message)
            else:
                message = (
                    f"Duplicate item. {box_item.human_readable_identifier} "
                    f"is already in position {box_item.position}."
                )
                messages.error(self.request, message)

    @property
    def box_href(self):
        url_name = url_names.get(self.post_action_url)
        return reverse(
            url_name,
            kwargs={"box_identifier": self.box_identifier, "action_name": "manage"},
        )

    def create_box_item(self):
        try:
            position = self.box.next_position
        except BoxIsFullError as e:
            message = format_html("{}", str(e))
            messages.error(self.request, message)
        else:
            box_item = BoxItem(
                box=self.box, identifier=self.box_item_identifier, position=position
            )
            box_item.save()
            if self.box.verified:
                self.box.save()
