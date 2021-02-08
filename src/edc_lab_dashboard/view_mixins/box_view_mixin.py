from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape
from django.views.generic.base import ContextMixin
from edc_lab.models import Aliquot, Box, BoxItem


class BoxViewError(Exception):
    pass


class BoxViewMixin(ContextMixin):

    """Declare with the ModelsViewMixin."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._box = None
        self._box_item = None
        self._box_identifier = None
        self._box_item_identifier = None
        self.original_box_item_identifier = None
        self.original_box_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "box_identifier": self.original_box_identifier,
                "box_item_identifier": self.original_box_item_identifier,
                "box": self.box,
                "paginator_url_kwargs": self.url_kwargs,
            }
        )
        return context

    @property
    def box_identifier(self):
        """Returns a cleaned box identifier."""
        if not self._box_identifier:
            self.original_box_identifier = escape(self.kwargs.get("box_identifier")).strip()
            self._box_identifier = "".join(self.original_box_identifier.split("-"))
        return self._box_identifier

    @property
    def box_item_identifier(self):
        """Returns a cleaned box_item_identifier or None."""
        if not self._box_item_identifier:
            self.original_box_item_identifier = escape(
                self.request.POST.get("box_item_identifier", "")
            ).strip()
            if self.original_box_item_identifier:
                self._box_item_identifier = self._clean_box_item_identifier()
        return self._box_item_identifier

    @property
    def box(self):
        if not self._box:
            if self.box_identifier:
                try:
                    self._box = Box.objects.get(box_identifier=self.box_identifier)
                except ObjectDoesNotExist:
                    self._box = None
        return self._box

    @property
    def box_item(self):
        """Returns a box item model instance."""
        if not self._box_item:
            if self.box_item_identifier:
                try:
                    self._box_item = BoxItem.objects.get(
                        box=self.box, identifier=self.box_item_identifier
                    )
                except ObjectDoesNotExist:
                    message = "Invalid box item. Got {}".format(
                        self.original_box_item_identifier
                    )
                    messages.error(self.request, message)
        return self._box_item

    def get_box_item(self, position):
        """Returns a box item model instance for the given position."""
        try:
            box_item = BoxItem.objects.get(box=self.box, position=position)
        except ObjectDoesNotExist:
            message = "Invalid position for box. Got {}".format(position)
            messages.error(self.request, message)
            return None
        return box_item

    def _clean_box_item_identifier(self):
        """Returns a valid identifier or raises."""
        box_item_identifier = "".join(self.original_box_item_identifier.split("-"))
        try:
            obj = Aliquot.objects.get(aliquot_identifier=box_item_identifier)
        except ObjectDoesNotExist:
            message = "Invalid aliquot identifier. Got {}.".format(
                self.original_box_item_identifier or "None"
            )
            messages.error(self.request, message)
            # raise BoxViewError(message)
        else:
            if obj.is_primary and not self.box.accept_primary:
                message = 'Box does not accept "primary" specimens. Got {} is primary.'.format(
                    self.original_box_item_identifier
                )
                messages.error(self.request, message)
                # raise BoxViewError(message)
            elif obj.numeric_code not in self.box.specimen_types.split(","):
                message = (
                    "Invalid specimen type. Box accepts types {}. "
                    "Got {} is type {}.".format(
                        ", ".join(self.box.specimen_types.split(",")),
                        self.original_box_item_identifier,
                        obj.numeric_code,
                    )
                )
                messages.error(self.request, message)
                # raise BoxViewError(message)
        return box_item_identifier
