import cups

from django.test import TestCase

from edc_label.label import Label, app_config
from edc_label.print_server import PrintServer


class DummyPrintServer(PrintServer):

    test_no_server = False
    test_no_printer = False

    def connect(self):
        if self.test_no_server:
            raise cups.IPPError
        return None

    @property
    def printers(self):
        return {
            'dummy_printer': {'printer-info': 'Dummy Printer'},
            'real_dummy_printer': {'printer-info': 'Real Dummy Printer'}
        }

    def print_file(self, *args):
        if self.test_no_printer:
            raise cups.IPPError('Some printer error, huh?')
        return 100


class LabelTests(TestCase):

    def setUp(self):
        DummyPrintServer.test_no_server = False
        app_config.default_printer_label = 'dummy_printer'

    def test_print_server(self):
        """Connects to default CUPS server (localhost).

        Assumes a CUPS server exists on localhost."""
        print_server = PrintServer()

    def test_label(self):
        """Assert labels were printed and job ids returned as per number of copies requested."""
        context = {'erik': 'erik'}
        label = Label(context, 'default', print_server_cls=DummyPrintServer)
        label.print_label(1)
        self.assertEqual(len(label.job_ids), 1)
        label.print_label(3)
        self.assertEqual(len(label.job_ids), 3)

    def test_printer(self):
        context = {'erik': 'erik'}
        label = Label(context, 'aliquot', print_server_cls=DummyPrintServer)
        self.assertEqual(str(label), 'dummy_printer@localhost')
        self.assertEqual(list(label.printer.keys()), ['dummy_printer'])

    def test_label_no_server(self):
        """Assert handles printer not found."""
        DummyPrintServer.test_no_server = True
        context = {'erik': 'erik'}
        label = Label(context, 'requisition', print_server_cls=DummyPrintServer)
        self.assertIn('Unable to connect to CUPS', label.error_message or '')
        label.print_label(1)
        self.assertIn('Unable to connect to CUPS', label.error_message or '')

    def test_label_no_printer(self):
        """Assert handles printer not found."""
        DummyPrintServer.test_no_printer = True
        context = {'erik': 'erik'}
        label = Label(context, 'requisition', print_server_cls=DummyPrintServer)
        label.print_label(1)
        self.assertIn('Unable to print', label.error_message or '')

    def test_label_wrong_printer(self):
        """Assert handles printer not found."""
        context = {'erik': 'erik'}
        label = Label(context, 'requisition', print_server_cls=DummyPrintServer, printer_name='erik')
        self.assertIn('not found on CUPS server', label.error_message)
        label.print_label(1)
        self.assertIn('Unable to print', label.error_message)
