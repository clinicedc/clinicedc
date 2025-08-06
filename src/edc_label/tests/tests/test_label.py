from django.test import TestCase

from ...printer import Printer


class DummyCupsConnection:
    printer_name = "test_printer"

    properties = {"printer-state-reasons": [""]}

    def getPrinters(self):
        return {self.printer_name: self.properties}

    def createJob(self, *args):
        return 1

    def startDocument(self, *args):
        return 1

    def writeRequestData(self, *args):
        return 1

    def finishDocument(self, *args):
        return 1


class TestLabels(TestCase):
    def test_dummy(self):
        connection = DummyCupsConnection()
        connection.getPrinters().get("test_printer")

    def test_str(self):
        printer = Printer(name="test_printer", print_server_func=DummyCupsConnection)
        self.assertTrue(str(printer))

    def test_repr(self):
        printer = Printer(name="test_printer", print_server_func=DummyCupsConnection)
        self.assertTrue(repr(printer))

    def test_stream_job(self):
        printer = Printer(name="test_printer", print_server_func=DummyCupsConnection)
        zpl_data = {}
        jobid = printer.stream_print(zpl_data)
        self.assertIsNotNone(jobid)
