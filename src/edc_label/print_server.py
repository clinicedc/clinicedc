import cups

from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_label')


# class PrintServerError(Exception):
#     pass


class Printer:

    label = None
    full_name = None
    verbose_name = None
    data = None

    def __str__(self):
        return self.verbose_name


class PrintServer:

    """ A simple wrapper for a few common cups methods.

    All cups attributes are still available from the connection
    object `print_server.conn`.
    """

    def __init__(self, cups_server_ip=None):
        self.conn = None
        self.error_message = []
        self.selected_printer = Printer()
        self.ip_address = cups_server_ip or app_config.default_cups_server_ip
        try:
            self.conn = self.connect()
        except (cups.IPPError, RuntimeError) as e:
            self.error_message.append(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def __str__(self):
        return self.ip_address or 'localhost'

    def connect(self):
        if self.ip_address == 'localhost' or self.ip_address is None:
            return cups.Connection()
        else:
            return cups.Connection(self.ip_address)

    @property
    def printers(self):
        """Return all printers from for CUPS.getPrinter()."""
        try:
            return self.conn.getPrinters()
        except cups.IPPError as e:
            self.error_message.append(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def select_printer(self, label):
        if not label:
            raise TypeError('Attribute \'label\' cannot be None')
        try:
            printer = self.get_printer(label)
            self.selected_printer.data = printer.get(label)
            self.selected_printer.label = label
            self.selected_printer.full_name = '{}@{}'.format(label, str(self))
            self.selected_printer.verbose_name = self.selected_printer.data.get('printer-info')
        except KeyError:
            self.error_message.append(
                'Printer \'{}\' not found on \'{}\'.'.format(label, str(self)))

    def get_printer(self, label):
        """Return a dictionary for one printer by label from CUPS.getPrinter()."""
        return {label: self.printers[label]}

    def print_file(self, *args):
        return self.conn.printFile(*args)

    @property
    def jobs(self):
        try:
            return self.conn.getJobs()
        except cups.IPPError as e:
            self.error_message.append(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def cancelJobs(self, job_ids):
        try:
            for job_id in job_ids:
                self.conn.cancelJob(job_id)
        except cups.IPPError as e:
            self.error_message.append(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))
