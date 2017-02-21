from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin


class IdentifierDoesNotExist(Exception):
    pass


class BoxItemView(EdcBaseViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab/home.html'
    navbar_name = 'specimens'
    box_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_model.split('.'))
    box_item_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').box_item_model.split('.'))
    add = False
    delete = False
    box_identifier = None
    box_item_identifier = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.selected_box_items = request.POST.getlist('box_items')
        self.box_item_identifier = escape(
            request.POST.get('box_item_identifier')).strip()
        self.box_identifier = ''.join(
            escape(request.POST.get('box_identifier')).strip().split('-'))
        self.box = self.box_model.objects.get(
            box_identifier=self.box_identifier)
        if request.POST.get('box_action') == 'add_item':
            self.add_box_item(request)
        elif request.POST.get('box_action') == 'renumber_items':
            self.renumber_items(request)
        elif request.POST.get('box_action') == 'remove_selected_items':
            self.remove_selected_items(request)
        url = reverse(
            django_apps.get_app_config('edc_lab').box_listboard_url_name,
            kwargs={'box_identifier': self.box_identifier})
        return HttpResponseRedirect(url)

    def remove_selected_items(self, request):
        if not self.selected_box_items:
            message = ('Nothing to do. No items have been selected.')
            messages.warning(request, message)
        else:
            deleted = self.box_item_model.objects.filter(
                pk__in=self.selected_box_items).delete()
            message = ('{} items have been removed.'.format(deleted[0]))
            messages.success(request, message)

    def renumber_items(self, request):
        box_items = self.box.boxitem_set.all().order_by('position')
        if box_items.count() == 0:
            message = ('Nothing to do. There are no items in the box.')
            messages.warning(request, message)
        else:
            for index, boxitem in enumerate(
                    self.box.boxitem_set.all().order_by('position'), start=1):
                boxitem.position = index
                boxitem.save()
            message = ('Box {} has been renumber. Be sure to physically verify '
                       'the position of each specimen.'.format(
                           self.box_identifier))
            messages.success(request, message)

    def add_box_item(self, request, **kwargs):
        """Adds the item to the next available position in the box.
        """
        if self.box_item_identifier:
            try:
                box_item_identifier = self.validate_identifier(
                    request, box=self.box)
                obj = self.box_item_model.objects.get(
                    box__box_identifier=self.box_identifier,
                    identifier=box_item_identifier)
            except self.box_item_model.DoesNotExist:
                obj = self.box_item_model(
                    box=self.box,
                    identifier=box_item_identifier,
                    position=self.box.next_position)
                obj.save()
            except IdentifierDoesNotExist:
                pass
            else:
                message = 'Duplicate item. {} is already in position {}.'.format(
                    self.box_item_identifier, obj.position)
                messages.error(request, message)

    def validate_identifier(self, request, box=None):
        """Returns a valid identifier or raises.
        """
        aliqout_model = django_apps.get_model(
            *django_apps.get_app_config('edc_lab').aliquot_model.split('.'))
        box_item_identifier = ''.join(self.box_item_identifier.split('-'))
        try:
            obj = aliqout_model.objects.get(
                aliquot_identifier=box_item_identifier)
        except aliqout_model.DoesNotExist:
            message = 'Invalid aliquot identifier. Got {}.'.format(
                self.box_item_identifier.strip())
            messages.error(request, message)
            raise IdentifierDoesNotExist()
        if obj.is_primary and not box.accept_primary:
            message = 'Box does not accept "primary" specimens. Got {} is primary.'.format(
                self.box_item_identifier.strip())
            messages.error(request, message)
            raise IdentifierDoesNotExist()
        elif obj.aliquot_type not in box.specimen_types.split(','):
            message = (
                'Invalid specimen type. Box accepts types {}. '
                'Got {} is type {}.'.format(
                    ', '.join(box.specimen_types.split(',')),
                    self.box_item_identifier,
                    obj.aliquot_type))
            messages.error(request, message)
            raise IdentifierDoesNotExist()
        return box_item_identifier
