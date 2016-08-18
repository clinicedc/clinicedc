from django.test import TestCase

from edc_label.label import Label, app_config
from edc_label.print_server import PrintServer, PrintServerError


class DummyPrintServer(PrintServer):

    test_no_printer = False

    def __init__(self, cups_server_ip=None):
        self.ip_address = cups_server_ip or app_config.default_cups_server_ip or 'localhost'

    @property
    def printers(self):
        if self.test_no_printer:
            raise PrintServerError('no printer server')
        return {
            'dummy_printer': {'printer-info': 'Dummy Printer'},
            'real_dummy_printer': {'printer-info': 'Real Dummy Printer'}
        }

    def get_printer(self, name):
        return {name: self.printers[name]}

    def print_file(self, *args):
        return 100


class LabelTests(TestCase):

    def setUp(self):
        DummyPrintServer.test_no_printer = False

    def test_print_server(self):
        """Connects to default CUPS server (localhost).

        Assumes a CUPS server exists on localhost."""
        print_server = PrintServer()

    def test_label(self):
        """Assert labels were printed and job ids returned as per number of copies requested."""
        context = {'erik': 'erik'}
        label = Label(context, print_server_cls=DummyPrintServer, printer_name='dummy_printer')
        label.print_label(1)
        self.assertEqual(len(label.job_ids), 1)
        label.print_label(3)
        self.assertEqual(len(label.job_ids), 3)

    def test_printer(self):
        context = {'erik': 'erik'}
        label = Label(context, print_server_cls=DummyPrintServer, printer_name='dummy_printer')
        self.assertEqual(str(label), 'dummy_printer@localhost')
        self.assertEqual(list(label.printer.keys()), ['dummy_printer'])

    def test_label_no_printer(self):
        """Assert handles printer not found."""
        DummyPrintServer.test_no_printer = True
        context = {'erik': 'erik'}
        label = Label(context, print_server_cls=DummyPrintServer)
        label.print_label(1)
        self.assertTrue(label.error_message)
