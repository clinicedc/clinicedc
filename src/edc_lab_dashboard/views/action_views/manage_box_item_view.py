from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from edc_lab.constants import SHIPPED
from edc_lab.exceptions import SpecimenError

from ..mixins import BoxViewMixin
from .base_action_view import BaseActionView


app_config = django_apps.get_app_config('edc_lab_dashboard')


class ManageBoxItemView(BoxViewMixin, BaseActionView):

    post_url_name = app_config.manage_box_listboard_url_name
    listboard_url_name = app_config.manage_box_listboard_url_name
    valid_form_actions = [
        'add_item', 'renumber_items', 'remove_selected_items']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def url_kwargs(self):
        return {
            'action_name': self.kwargs.get('action_name'),
            'box_identifier': self.box_identifier}

    def process_form_action(self):
        if self.action == 'add_item':
            try:
                if self.box_item_identifier:
                    self.add_box_item()
            except SpecimenError:
                pass
        elif self.action == 'renumber_items':
            self.renumber_items()
        elif self.action == 'remove_selected_items':
            self.remove_selected_items()

    def remove_selected_items(self):
        """Deletes the selected items.
        """
        if not self.selected_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(self.request, message)
        elif self.box.status == SHIPPED:
            message = ('Unable to remove. Box has already been shipped.')
            messages.error(self.request, message)
        else:
            deleted = self.box_item_model.objects.filter(
                pk__in=self.selected_items,
            ).exclude(box__status=SHIPPED).delete()
            message = ('{} items have been removed.'.format(deleted[0]))
            messages.success(self.request, message)

    def renumber_items(self):
        """Resets positions to be a sequence incremented by 1.
        """
        box_items = self.box.boxitem_set.all().order_by('position')
        if box_items.count() == 0:
            message = ('Nothing to do. There are no items in the box.')
            messages.warning(self.request, message)
        elif self.box.status == SHIPPED:
            message = ('Unable to renumber. Box has already been shipped.')
            messages.error(self.request, message)
        else:
            for index, boxitem in enumerate(
                    self.box.boxitem_set.all().order_by('position'), start=1):
                boxitem.position = index
                boxitem.verified = False
                boxitem.verified_datetime = None
                boxitem.save()
            self.box.save()
            message = ('Box {} has been renumber. Be sure to verify '
                       'the position of each specimen.'.format(
                           self.box_identifier))
            messages.success(self.request, message)

    def add_box_item(self, **kwargs):
        """Adds the item to the next available position in the box.
        """
        if self.box.status == SHIPPED:
            message = ('Unable to add. Box has already been shipped.')
            messages.error(self.request, message)
        else:
            try:
                box_item = self.box_item_model.objects.get(
                    box__box_identifier=self.box_identifier,
                    identifier=self.box_item_identifier)
            except self.box_item_model.DoesNotExist:
                try:
                    box_item = self.box_item_model.objects.get(
                        identifier=self.box_item_identifier)
                except self.box_item_model.DoesNotExist:
                    box_item = self.box_item_model(
                        box=self.box,
                        identifier=self.box_item_identifier,
                        position=self.box.next_position)
                    box_item.save()
                    if self.box.verified:
                        self.box.save()
                else:
                    message = mark_safe(
                        'Item is already packed. See box <a href="{href}" class="alert-link">'
                        '{box_identifier}</a>'.format(
                            href=reverse(
                                self.listboard_url_name,
                                kwargs={
                                    'box_identifier': box_item.box.box_identifier,
                                    'action_name': 'manage'}),
                            box_identifier=box_item.box.human_readable_identifier))
                    messages.error(self.request, message)
            else:
                message = 'Duplicate item. {} is already in position {}.'.format(
                    box_item.human_readable_identifier, box_item.position)
                messages.error(self.request, message)
