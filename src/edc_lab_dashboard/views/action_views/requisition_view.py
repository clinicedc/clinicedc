from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_lab.labels import AliquotLabel

from .action_view import ActionView


class RequisitionView(ActionView):

    post_action_url = 'requisition_listboard_url'
    valid_form_actions = ['print_labels']
    action_name = 'requisition'
    label_cls = AliquotLabel

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def process_form_action(self):
        print('hello1')
        if self.action == 'print_labels':
            print('hello2')
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
                    f'processed. Got {requisition.requisition_identifier}')

    @property
    def requisitions(self):
        return self.requisition_model.objects.filter(
            processed=True, pk__in=self.selected_items)
