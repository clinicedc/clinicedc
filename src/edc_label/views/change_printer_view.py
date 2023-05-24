from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views.generic.edit import ProcessFormView
from edc_auth.models import UserProfile

from ..constants import (
    CLINIC_LABEL_PRINTER_NAME,
    LAB_LABEL_PRINTER_NAME,
    PRINT_SERVER_NAME,
)


class ChangePrinterView(LoginRequiredMixin, ProcessFormView):
    success_url = "edc_label:home_url"
    empty_selection = "--"

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=self.request.user)

        print_server_name = request.POST.get(PRINT_SERVER_NAME)
        if print_server_name:
            if print_server_name == self.empty_selection:
                print_server_name = None
            request.session[PRINT_SERVER_NAME] = print_server_name
            user_profile.print_server = print_server_name

        clinic_label_printer_name = request.POST.get(CLINIC_LABEL_PRINTER_NAME)
        if clinic_label_printer_name:
            if clinic_label_printer_name == self.empty_selection:
                clinic_label_printer_name = None
            request.session[CLINIC_LABEL_PRINTER_NAME] = clinic_label_printer_name
            user_profile.clinic_label_printer = clinic_label_printer_name

        lab_label_printer_name = request.POST.get(LAB_LABEL_PRINTER_NAME)
        if lab_label_printer_name:
            if lab_label_printer_name == self.empty_selection:
                lab_label_printer_name = None
            request.session[LAB_LABEL_PRINTER_NAME] = lab_label_printer_name
            user_profile.lab_label_printer = lab_label_printer_name

        user_profile.save()
        success_url = reverse(self.success_url)

        return HttpResponseRedirect(redirect_to=success_url)
