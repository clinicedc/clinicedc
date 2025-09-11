from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views.generic.edit import ProcessFormView

from ..job_result import JobResult
from ..label import Label
from ..printers_mixin import PrintersMixin


class PrintLabelView(LoginRequiredMixin, PrintersMixin, ProcessFormView):
    success_url = "edc_label:home_url"
    label_cls = Label
    job_result_cls = JobResult

    def post(self, request, *args, **kwargs):
        printer_name = request.POST.get("printer_name")
        label_template_name = request.POST.get("label_template_name")
        printer = self.printers.get(printer_name)
        if printer.printer_state_message:
            messages.warning(request, f"{printer.name}: {printer.printer_state_message}")
        label = self.label_cls(label_template_name=label_template_name)
        zpl_data = label.render_as_zpl_data(copies=3, context={})
        job_id = printer.stream_print(zpl_data=zpl_data)
        job_result = self.job_result_cls(
            name=label_template_name, copies=1, job_ids=[job_id], printer=printer
        )
        messages.success(request, job_result.message)
        success_url = reverse(self.success_url)
        return HttpResponseRedirect(redirect_to=success_url)
