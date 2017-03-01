import tempfile

from django.apps import apps as django_apps
from django.utils import timezone

from .exceptions import PrintLabelError
from .label_template import LabelTemplate
from .print_server import PrintServer


class Label:

    """A class that prepares and prints copies of labels.
    """
    template_name = None

    def __init__(self, template_name=None, print_server=None, printer_name=None):
        if template_name:
            self.template_name = template_name
        self.conn = None
        self.job_ids = []
        self.messages = None
        # will default to localhost
        app_config = django_apps.get_app_config('edc_label')
        self.print_server = print_server or PrintServer()
        self.print_server.select_printer(
            printer_name or app_config.default_printer_name)
        if self.print_server.error_message:
            self.error_message = self.print_server.error_message

    def __str__(self):
        return self.print_server.selected_printer.full_name

    @property
    def label_name(self):
        return 'label'

    @property
    def context(self):
        return {}

    def print_label(self, copies=None, context=None):
        """ Prints the label or fails silently with a message. """
        self.messages = {'success': [], 'error': []}
        job_ids = []
        copies = copies or 1
        context = context or self.context
        rendered_label = LabelTemplate(
            template_name=self.template_name).render(context)
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        for i in range(copies, 0, -1):
            context.update({
                'label_count': i,
                'label_count_total': copies,
                'timestamp': timestamp})
            _, filename = tempfile.mkstemp()  # create temp file
            with open(filename, 'w') as f:
                f.write(rendered_label)
            #  note: "raw" attr is to prevent CUPS from rendering
            job_id = self.print_server.print_file(
                self.print_server.selected_printer.label,
                filename, 'edc_label',
                {'raw': filename})
            if not job_id:
                raise PrintLabelError('Print job failed. No printer selected.')
            job_ids.append(job_id)
        return {'name': self.label_name,
                'print_count': len(job_ids),
                'copies': copies,
                'printer': self.print_server.selected_printer.full_name,
                'jobid': ','.join([str(i) for i in self.job_ids or [0]])}
