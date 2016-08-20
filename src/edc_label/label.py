import tempfile

from django.apps import apps as django_apps
from django.utils import timezone
from edc_label.print_server import PrintServer

app_config = django_apps.get_app_config('edc_label')


class Label:

    """A class that prepares and prints copies of labels."""

    def __init__(self, label_name, print_server=None, printer_name=None, context=None,
                 label_identifier_name=None):
        self.conn = None
        self.error_message = []
        self.job_ids = []
        self.label_commands = None
        self.message = None
        self.label_identifier_name = label_identifier_name or app_config.default_label_identifier_name
        self.test_context = {}
        self.context = context
        self.label_name = label_name
        self.print_server = print_server or PrintServer()  # will default to localhost
        self.print_server.select_printer(printer_name or app_config.default_printer_label)
        if self.print_server.error_message:
            self.error_message = self.print_server.error_message

    def __str__(self):
        return self.print_server.selected_printer.full_name

    def print_label(self, copies=None, context=None, label_identifier_name=None):
        """ Prints the label or fails silently with a message. """
        copies = copies or 1
        if label_identifier_name:
            self.label_identifier_name = label_identifier_name
        self.error_message, self.message = None, None
        if context:
            self.context.update(context)
        self.label_commands = app_config.label_templates[self.label_name].render(self.context)
        self.job_ids = []
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        for i in range(copies, 0, -1):
            self.context.update({
                'label_count': i,
                'label_count_total': copies,
                'timestamp': timestamp})
            _, filename = tempfile.mkstemp()  # create temp file
            with open(filename, 'w') as f:
                f.write(self.label_commands)
            #  note: "raw" attr is to prevent CUPS from rendering
            job_id = self.print_server.print_file(
                self.print_server.selected_printer.label, filename, "edc_label", {'raw': filename})
            if job_id:
                self.job_ids.append(job_id)
            else:
                self.error_message = 'Print job failed. No printer selected.'
                break
            self.message = (
                'Successfully printed {1}/{2} label(s) {0} to '
                '{3} Job ID {4}'.format(
                    self.context.get(self.label_identifier_name, ''),
                    len(self.job_ids),
                    copies,
                    self.print_server.selected_printer,
                    ','.join([str(i) for i in self.job_ids])))
