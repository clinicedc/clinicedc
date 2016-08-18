import sys
import cups
import tempfile

from datetime import datetime

from django.apps import apps as django_apps

from .print_server import PrintServer, PrintServerError

app_config = django_apps.get_app_config('edc_label')


class Label:

    def __init__(self, context, label_name, printer_name=None,
                 cups_server_ip=None, label_identifier_name=None,
                 print_server_cls=None):
        printer_name = printer_name or app_config.default_printer_label
        self.conn = None
        self.context = context
        self.error_message = None
        self.filename = None
        self.job_ids = []
        self.label_identifier_name = label_identifier_name or app_config.default_label_identifier_name
        self.message = None
        self.print_server_cls = print_server_cls or PrintServer
        self.print_server = None
        self.printer = None

        try:
            self.print_server = self.print_server_cls(cups_server_ip)
            self.printer = self.print_server.get_printer(printer_name)
        except PrintServerError as e:
            self.error_message = str(e)
        self.label = app_config.label_templates[label_name].render(context)
        _, self.filename = tempfile.mkstemp()
        if self.error_message:
            sys.stdout.write(self.error_message + '\n')

    def __str__(self):
        return '{}@{}'.format(self.printer_name, self.print_server or 'localhost')

    @property
    def printer_name(self):
        try:
            return list(self.printer.keys())[0]
        except AttributeError:
            return None

    def print_label(self, copies):
        """ Prints the label or fails silently with a message. """
        copies = copies or 1
        # reverse order so labels are in order top to bottom on a strip
        self.job_ids = []
        for i in range(copies, 0, -1):
            self.context.update({
                'label_count': i,
                'label_count_total': copies,
                'timestamp': datetime.today().strftime('%Y-%m-%d %H:%M')})
            with open(self.filename, 'w') as f:
                f.write(self.label)
            try:
                self.job_ids.append(
                    self.print_server.print_file(
                        self.printer_name, self.filename, "edc_label", {'raw': self.filename}))  # don't let CUPS render!
            except AttributeError:
                break
            except (cups.IPPError, RuntimeError) as e:
                self.error_message = (
                    'Unable to print to {}@{}. Got \'{}\'').format(
                        self.printer_name, self.print_server, str(e))
                sys.stdout.write(self.error_message + '\n')
                break
            self.message = (
                'Successfully printed {1}/{2} label(s) {0} to '
                '{3}@{4} Job ID {5}'.format(
                    self.context.get(self.label_identifier_name, ''),
                    len(self.job_ids),
                    copies,
                    self.printer_name,
                    self.print_server,
                    ','.join([str(i) for i in self.job_ids])))
