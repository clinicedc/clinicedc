from django.views.generic.base import TemplateView

from edc_base.views.edc_base_view_mixin import EdcBaseViewMixin
from edc_label.print_server import PrintServer, PrintServerError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_label.label import app_config


class HomeView(EdcBaseViewMixin, TemplateView):

    template_name = 'edc_label/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        print_server_error = None
        try:
            print_server = PrintServer()
        except PrintServerError as e:
            print_server = {}
            print_server_error = str(e)
        printers = {}
        if print_server:
            for printer in print_server.printers.items():
                printer = str(printer[0])
                printer_properties = {k.replace('-', '_'): v for k, v in print_server.printers[printer].items()}
                printers.update({printer: printer_properties})
        context.update({
            'project_name': '{}: {}'.format(context.get('project_name'), app_config.verbose_name),
            'label_templates': app_config.label_templates,
            'print_server': print_server,
            'print_server_error': print_server_error,
            'default_printer_label': app_config.default_printer_label,
            'printers': printers,
            'selected_printer': None
        })
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)
