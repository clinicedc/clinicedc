from django.contrib import messages
from django.views.generic.base import ContextMixin

from .printers_mixin import PrinterError, PrintersMixin, PrintServerError


class EdcLabelViewMixin(PrintersMixin, ContextMixin):
    error_messages = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(print_servers=self.print_servers)
        try:
            context.update(selected_print_server_name=self.print_server_name)
        except PrintServerError as e:
            messages.error(self.request, str(e))
        else:
            try:
                context.update(printers=self.printers)
            except (PrintServerError, PrinterError) as e:
                messages.error(self.request, str(e))
            else:
                try:
                    context.update(selected_clinic_label_printer=self.clinic_label_printer)
                except PrinterError:
                    pass
                try:
                    context.update(selected_lab_label_printer=self.lab_label_printer)
                except PrinterError:
                    pass
        error_messages = list(set(self.error_messages))
        for message in error_messages:
            messages.error(self.request, message)
        return context
