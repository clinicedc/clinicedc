import cups

from django.apps import apps as django_apps
from django.test import TestCase, tag
from pprint import pprint
from edc_label.print_server import PrinterError
from django.urls.base import reverse
from django.test.client import RequestFactory

from ..label import Label
from ..label_template import LabelTemplate, LabelTemplateError
from ..labeler import Labeler
from ..print_server import PrintServer, Printer, PrintServerSelectPrinterError


class DummyPrintServer(PrintServer):

    test_no_server = False
    test_no_printer = False

    def connect(self):
        if self.test_no_server:
            raise cups.IPPError
        return None

    @property
    def get_printer_properties(self, printer_name=None):
        properties = {
            'dummy_printer': {'printer-info': 'Dummy Printer'},
            'real_dummy_printer': {'printer-info': 'Real Dummy Printer'}
        }
        return properties.get(printer_name)

    def print_file(self, *args):
        if not self.selected_printer.printer_name:
            return None
        return 100

    @property
    def selected_printer(self):
        return self._selected_printer

    @selected_printer.setter
    def selected_printer(self, printer_name=None):
        self._selected_printer = Printer()


class DummyLabel(Label):

    print_server_cls = DummyPrintServer

    def print_label(self, copies=None, context=None):
        self.job_ids = [n for n in range(0, copies)]
        return None


class TestLabels(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_label')
        DummyPrintServer.test_no_server = False
        DummyPrintServer.test_no_printer = False
        app_config.default_printer_name = 'dummy_printer'

    def test_print_server(self):
        """Connects to default CUPS server (localhost).

        Assumes a CUPS server exists on localhost.
        """
        self.assertTrue(PrintServer())
        self.assertTrue(PrintServer(printer_name=None))
        self.assertRaises(
            PrintServerSelectPrinterError,
            PrintServer, printer_name='blah')

    def test_print_server_conn(self):
        ps = PrintServer()
        ps.connect()
        self.assertIsNone(ps.error_message)

    def test_print_server_get_printers(self):
        ps = PrintServer()
        self.assertTrue(ps.printers)

    def test_print_server_get_properties(self):
        ps = PrintServer()
        pprint(ps.selected_printer.printer_data)

    def test_print_server_options(self):
        """Requires CUPS printer "home_label_printer".
        """
        ps = PrintServer()
        options = ps.to_dict()
        self.assertEqual(options.get('ip_address'), 'localhost')
        self.assertEqual(options.get('selected_printer'),
                         'home_label_printer@localhost')
        self.assertEqual(options.get('name'), 'localhost')

    def test_print_server_options2(self):
        """Requires CUPS printer "home_label_printer".
        """
        ps = PrintServer(printer_name='home_label_printer')
        options = ps.to_dict()
        self.assertEqual(options.get('ip_address'), 'localhost')
        self.assertEqual(options.get('selected_printer'),
                         'home_label_printer@localhost')
        self.assertEqual(options.get('name'), 'localhost')

    def test_printer_name(self):
        self.assertRaises(
            PrintServerSelectPrinterError,
            PrintServer, printer_name='blah')
        print_server = PrintServer(printer_name='home_label_printer')
        self.assertEqual(
            print_server.selected_printer.verbose_name, 'home_label_printer')

    def test_label(self):
        """Assert labels were printed and job ids returned as
        per number of copies requested.
        """
        context = {'name': 'Test Label'}
        Label.print_server_cls = PrintServer
        label = Label(template_name='default',
                      printer_name='home_label_printer')
        print_result = label.print_label(copies=1, context=context)
        self.assertEqual(print_result.print_count, 1)
        print_result = label.print_label(copies=3, context=context)
        self.assertEqual(print_result.print_count, 3)

    def test_label_template_no_template_name(self):
        self.assertRaises(
            LabelTemplateError,
            LabelTemplate)

    def test_context(self):
        context = {'name': 'Test1 Label'}
        label_template = LabelTemplate(template_name='default')
        rendered = label_template.render(context)
        self.assertIn('Test1 Label', rendered)

    def test_label_no_server(self):
        """Assert handles printer not found.
        """
        DummyPrintServer.test_no_server = True
        self.assertRaises(
            PrinterError,
            DummyPrintServer, printer_name='dummy_printer')

    def test_labeler(self):
        labeler = Labeler()
        self.assertIsNotNone(labeler.printers)

    def test_labeler_print(self):
        context = {'name': 'Test Label'}
        labeler = Labeler()
        labeler.print_label(template_name='requisition',
                            copies=1, context=context)

    @tag('1')
    def test_session_printer(self):
        context = {'name': 'Test Label'}
        self.client.get(reverse('home_url'))
        session = self.client.session
        session['session_label_printer'] = 'home_label_printer'
        request = RequestFactory()
        request.session = session
        labeler = Labeler(request=request)
        labeler.print_label(template_name='requisition',
                            copies=1, context=context)
        session['session_label_printer'] = 'blah'
        request = RequestFactory()
        request.session = session
        self.assertRaises(
            PrintServerSelectPrinterError,
            Labeler, request=request)
