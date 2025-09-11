import os
import tempfile
from uuid import uuid4

import cups


class PrinterError(Exception):
    pass


class Printer:
    """A simple wrapper of a CUPS printer description.

    The CUPS printer description is a value from the mapping
    returned by getPrinters()

    * Replaces "-" with "_" in key names
    * Adds extra properties and methods.
    """

    def __init__(
        self,
        name=None,
        print_server_func=None,
        print_server_ip=None,
        print_server_name=None,
    ):
        self.name = name
        self.printer_info = None
        self.printer_make_and_model = None
        self.print_server = print_server_func
        self.print_server_name = print_server_name
        self.print_server_ip = print_server_ip
        cups_connection = print_server_func()
        try:
            cups_properties = cups_connection.getPrinters().get(name)
        except cups.IPPError:
            pass
        else:
            for k, v in cups_properties.items():
                k = k.replace("-", "_")
                setattr(self, k, v)
        self.printer_state_reasons = [r for r in self.printer_state_reasons if r != "none"]
        if self.printer_state_reasons:
            self.printer_state_reasons = ", ".join(self.printer_state_reasons)

    def __str__(self):
        return f"{self.printer_info or self.name} ({self.printer_make_and_model})"

    def __repr__(self):
        return f"{self.__class__}(name={self.name})"

    def stream_print(self, zpl_data=None):
        """Returns a job_id after sending zpl_data
        to the printer.
        """
        cups_connection = self.print_server()
        try:
            job_id = cups_connection.createJob(self.name, "", {})
            cups_connection.startDocument(
                self.name, job_id, str(uuid4()), cups.CUPS_FORMAT_RAW, 1
            )
            cups_connection.writeRequestData(zpl_data, len(zpl_data))
            cups_connection.finishDocument(self.name)
        except cups.IPPError as e:
            raise PrinterError(f"Failed to print. Tried printing to '{self.name}'. Got '{e}'.")
        return job_id

    def print_file(self, zpl_data=None):
        """Returns a job_id after sending zpl_data
        to the printer (uses printFile).
        """
        job_id = None
        _, temp = tempfile.mkstemp()
        cups_connection = self.print_server()
        try:
            with open(temp, "w") as f:
                f.write(zpl_data)
            #  note: "raw" attr is to prevent CUPS from rendering
            args = (self.name, temp, "edc_label", {"raw": temp})
            try:
                job_id = cups_connection.printFile(*args)
            except cups.IPPError as e:
                raise PrinterError(f"{e} using options {args}.")
        finally:
            os.remove(temp)
        return job_id
