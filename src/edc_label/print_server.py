import cups
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()
app_config = django_apps.get_app_config('edc_label')


class PrintServerError(Exception):
    pass


class PrintServerSelectPrinterError(Exception):
    pass


class PrinterError(Exception):
    pass


class Printer:

    def __init__(self, printer_name=None, printer_data=None, print_server=None):
        if not printer_data:
            raise PrinterError(
                f'Unable to determine printer. Got printer_name={printer_name}.')
        else:
            self.printer_data = printer_data
            self.printer_name = printer_name
            self.full_name = f'{self.printer_name}@{print_server}'
            self.verbose_name = self.printer_data.get('printer-info')

    def __str__(self):
        return self.verbose_name


class PrintServer:

    """ A simple wrapper for a few common cups methods.

    All cups attributes are still available from the connection
    object `print_server.conn`.
    """

    connection_err_msg = 'Unable to connect to CUPS server {}. Got \'{}\''
    printer_err_msg = 'Printer \'{}\' not found on \'{}\'.'
    printer_cls = Printer
    cups_server_ip = app_config.default_cups_server_ip
    printer_name = app_config.default_printer_name
    session_printer_attr = 'session_label_printer'

    def __init__(self, cups_server_ip=None, printer_name=None, request=None):
        self._selected_printer = None
        self.conn = None
        self.error_message = None
        self.ip_address = cups_server_ip or self.cups_server_ip
        self.name = self.ip_address or 'localhost'
        try:
            self.conn = self.connect()
        except (cups.IPPError, RuntimeError) as e:
            sys.stdout.write(style.ERROR(f'{e}\n'))
            sys.stdout.flush()
            self.error_message = self.connection_err_msg.format(
                self.ip_address, str(e))
        try:
            session_printer = request.session.get(self.session_printer_attr)
        except AttributeError:
            session_printer = None
        self.printer_name = session_printer or printer_name or self.printer_name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'ip_address': self.ip_address or 'localhost',
            'selected_printer': self.selected_printer.full_name,
            'name': self.name}

    def connect(self):
        if self.ip_address == 'localhost' or self.ip_address is None:
            return cups.Connection()
        else:
            return cups.Connection(self.ip_address)

    @property
    def printers(self):
        """Return a dictionary all printers from for CUPS.getPrinter().
        """
        printers = {}
        try:
            printers = self.conn.getPrinters()
        except (AttributeError, cups.IPPError) as e:
            sys.stdout.write(style.WARNING(
                f'Unable to list printers from CUPS. Got {e}'))
            self.error_message = self.error_message or self.connection_err_msg.format(
                self.ip_address, str(e))
        return printers

    @property
    def selected_printer(self):
        """Select a printer by printer_name from those available on
        the CUPS server.
        """
        if not self._selected_printer:
            properties = self.get_printer_properties(self.printer_name)
            self._selected_printer = self.printer_cls(
                printer_name=self.printer_name,
                print_server=self,
                printer_data=properties)
        return self._selected_printer

    def get_printer_properties(self, printer_name=None):
        """Return a dictionary of one printer by label from
        CUPS.getPrinter().

        Note: dictionary items are added using the '_' in place
        of '-', e.g. after update both 'printer-info' and
        printer_info' are valid.
        """
        properties = None
        try:
            properties = self.printers[printer_name]
        except KeyError:
            if not printer_name:
                try:
                    printer_name = list(self.printers.keys())[0]
                except IndexError:
                    pass
                else:
                    properties = self.printers[printer_name]
        if not properties:
            raise PrintServerSelectPrinterError(
                f'Unable to select a printer. Printer \'{self.printer_name}\' not found. '
                f'Expected one of {list(self.printers.keys())}. '
                'See AppConfig.default_printer_name.')
        properties.update(
            {k.replace('-', '_'): v for k, v in properties.items()})
        return properties

    def print_file(self, *args):
        return self.conn.printFile(self.selected_printer.printer_name, *args)

    @property
    def jobs(self):
        try:
            return self.conn.getJobs()
        except cups.IPPError as e:
            self.error_message = self.error_message or self.connection_err_msg.format(
                self.ip_address, str(e))

    def cancelJobs(self, job_ids):
        try:
            for job_id in job_ids:
                self.conn.cancelJob(job_id)
        except cups.IPPError as e:
            self.error_message = self.error_message or self.connection_err_msg.format(
                self.ip_address, str(e))
