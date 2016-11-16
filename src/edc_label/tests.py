import cups

from django.apps import apps as django_apps
from django.test import TestCase

from .label import Label
from .print_server import PrintServer, Printer


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
        if not self.selected_printer.label:
            return None
        return 100


class LabelTests(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_label')
        DummyPrintServer.test_no_server = False
        DummyPrintServer.test_no_printer = False
        app_config.default_printer_label = 'dummy_printer'

    def test_print_server(self):
        """Connects to default CUPS server (localhost).

        Assumes a CUPS server exists on localhost."""
        PrintServer()

    def test_printer_name(self):
        print_server = DummyPrintServer()
        print_server.select_printer('dummy_printer')
        self.assertEqual(print_server.selected_printer.verbose_name, 'Dummy Printer')

    def test_label(self):
        """Assert labels were printed and job ids returned as per number of copies requested."""
        context = {'name': 'Test Label'}
        label = Label('default', context=context, print_server=DummyPrintServer(), printer_name='dummy_printer')
        label.print_label(1)
        self.assertEqual(len(label.job_ids), 1)
        label.print_label(3)
        self.assertEqual(len(label.job_ids), 3)

    def test_context(self):
        """Assert labels were printed and job ids returned as per number of copies requested."""
        context = {'name': 'Test1 Label'}
        label = Label('default', context=context, print_server=DummyPrintServer(), printer_name='dummy_printer')
        label.print_label(1)
        self.assertIn('Test1', label.label_commands)
        label.print_label(1, context={'name': 'Test2 Label'})
        self.assertIn('Test2', label.label_commands)

    def test_printer(self):
        context = {'name': 'Test Label'}
        label = Label('aliquot', context=context, print_server=DummyPrintServer())
        self.assertEqual(str(label), 'dummy_printer@localhost')
        self.assertEqual(label.print_server.selected_printer.label, 'dummy_printer')
        self.assertEqual(label.print_server.selected_printer.verbose_name, 'Dummy Printer')

    def test_label_no_server(self):
        """Assert handles printer not found."""
        DummyPrintServer.test_no_server = True
        context = {'name': 'Test Label'}
        label = Label('requisition', context=context, print_server=DummyPrintServer())
        self.assertIn('Unable to connect to CUPS', label.print_server.error_message)
        label.print_label(1)
        self.assertIn('Unable to connect to CUPS', label.print_server.error_message)

    def test_label_no_printer(self):
        """Assert handles printer not selected."""
        DummyPrintServer.test_no_printer = True
        context = {'name': 'Test Label'}
        label = Label('requisition', context=context, print_server=DummyPrintServer())
        label.print_server.selected_printer = Printer()
        label.print_label(1)
        self.assertIn('Print job failed. No printer selected.', label.error_message)
        self.assertEqual(len(label.job_ids), 0)

    def test_label_invalid_printer(self):
        """Assert handles printer not found."""
        context = {'name': 'Test Label'}
        label = Label('requisition', context=context, print_server=DummyPrintServer(), printer_name='invalid_printer')
        self.assertIn('Printer \'invalid_printer\' not found on \'localhost\'.', label.print_server.error_message)
        label.print_label(1)
        self.assertIn('Printer \'invalid_printer\' not found on \'localhost\'.', label.print_server.error_message)
