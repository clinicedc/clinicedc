import cups
import sys
import tempfile

from django.apps import apps as django_apps
from django.utils import timezone

from .print_server import PrintServer, PrintServerError

app_config = django_apps.get_app_config('edc_label')


class Label:

    """A class that prepares and prints copies of a single label."""

    def __init__(self, context, label_name, printer_name=None,
                 cups_server_ip=None, label_identifier_name=None,
                 print_server_cls=None):
        printer_name = printer_name or app_config.default_printer_label
        self.conn = None
        self.context = context
        self.test_context = {}
        self.error_message = None
        self.job_ids = []
        self.label_commands = None
        self.label_identifier_name = label_identifier_name or app_config.default_label_identifier_name
        self.label_name = label_name
        self.message = None
        self.print_server = None
        self.print_server_cls = print_server_cls or PrintServer
        self.printer = None
        try:
            self.print_server = self.print_server_cls(cups_server_ip)
            self.printer = self.print_server.get_printer(printer_name)
        except PrintServerError as e:
            self.error_message = str(e)
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

    def print_label(self, copies=None, **context_options):
        """ Prints the label or fails silently with a message. """
        copies = copies or 1
        self.context.update(**context_options)
        self.label_commands = app_config.label_templates[self.label_name].render(self.context)
        self.job_ids = []
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        # reverse order so labels are in order top to bottom on a strip
        for i in range(copies, 0, -1):
            # some default context options, if you want them
            self.context.update({
                'label_count': i,
                'label_count_total': copies,
                'timestamp': timestamp})
            # create temp file
            _, filename = tempfile.mkstemp()
            # write label commands to file
            with open(filename, 'w') as f:
                f.write(self.label_commands)
            try:
                # send to printer on CUPS server
                # "raw" attr is to prevent CUPS from rendering
                self.job_ids.append(
                    self.print_server.print_file(
                        self.printer_name, filename, "edc_label", {'raw': filename}))
            except TypeError as e:
                self.error_message = (
                    'Unable to print. No valid printer selected. Got \'{}\'').format(
                        self.printer_name, self.print_server, str(e))
                break
            except AttributeError:
                # jump out if print server is None
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
