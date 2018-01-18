from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import ProcessFormView
from django.urls.base import reverse
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from ..printers_mixin import PrintersMixin
from edc_label.label import Label


class PrintLabelView(LoginRequiredMixin, PrintersMixin, ProcessFormView):

    success_url = 'edc_label:home_url'

    def post(self, request, *args, **kwargs):

        printer_name = request.POST.get('printer_name')
        label_template_name = request.POST.get('label_template_name')

        printer = self.printers.get(printer_name)
        label = Label(label_template_name=label_template_name, printer=printer)
        job_result = label.print_label(copies=3, context={})
        messages.success(request, job_result.message)
        success_url = reverse(self.success_url)
        return HttpResponseRedirect(redirect_to=success_url)
