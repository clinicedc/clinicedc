from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import ProcessFormView
from django.urls.base import reverse
from django.http.response import HttpResponseRedirect

from ..constants import CLINIC_LABEL_PRINTER, LAB_LABEL_PRINTER, PRINT_SERVER
from edc_base.models import UserProfile


class ChangePrinterView(ProcessFormView):

    success_url = 'edc_label:home_url'
    empty_selection = '--'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        user_profile = UserProfile.objects.get(user=self.request.user)

        print_server = request.POST.get(PRINT_SERVER)
        if print_server:
            if print_server == self.empty_selection:
                print_server = None
            request.session[PRINT_SERVER] = print_server
            user_profile.print_server = print_server

        clinic_label_printer = request.POST.get(CLINIC_LABEL_PRINTER)
        if clinic_label_printer:
            if clinic_label_printer == self.empty_selection:
                clinic_label_printer = None
            request.session[CLINIC_LABEL_PRINTER] = clinic_label_printer
            user_profile.clinic_label_printer = clinic_label_printer

        lab_label_printer = request.POST.get(LAB_LABEL_PRINTER)
        if lab_label_printer:
            if lab_label_printer == self.empty_selection:
                lab_label_printer = None
            request.session[LAB_LABEL_PRINTER] = lab_label_printer
            user_profile.lab_label_printer = lab_label_printer

        user_profile.save()
        success_url = reverse(self.success_url)

        return HttpResponseRedirect(redirect_to=success_url)
