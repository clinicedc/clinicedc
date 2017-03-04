from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ...labels import AliquotLabel
from .base_action_view import BaseActionView, app_config


class RequisitionView(BaseActionView):

    post_url_name = app_config.requisition_listboard_url_name
    valid_form_actions = ['print_labels']
    action_name = 'requisition'
    label_class = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        if self.action == 'print_labels':
            for requisition in self.requisitions:
                aliquots = (
                    self.aliquot_model.objects.filter(
                        requisition_identifier=requisition.requisition_identifier)
                    .order_by('count'))
                if aliquots:
                    self.print_labels(
                        pks=[obj.pk for obj in aliquots if obj.is_primary])
                    self.print_labels(
                        pks=[obj.pk for obj in aliquots if not obj.is_primary])
            for requisition in self.requisition_model.objects.filter(
                    processed=False, pk__in=self.selected_items):
                messages.error(
                    self.request,
                    'Unable to print labels. Requisition has not been '
                    'processed. Got {}'.format(
                        requisition.requisition_identifier))

    @property
    def requisitions(self):
        return self.requisition_model.objects.filter(
            processed=True, pk__in=self.selected_items)
