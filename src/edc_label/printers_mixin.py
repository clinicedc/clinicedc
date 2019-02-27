import cups
import socket

from django.apps import apps as django_apps

from .printer import Printer


class PrinterError(Exception):
    pass


class PrintServerError(Exception):
    pass


class PrintersMixin:
    @property
    def user_profile(self):
        UserProfile = django_apps.get_model("edc_auth.userprofile")
        return UserProfile.objects.get(user=self.request.user)

    @property
    def print_server_name(self):
        """Returns a string.
        """
        return self.request.session.get(
            "print_server_name", self.user_profile.print_server
        )

    @property
    def clinic_label_printer_name(self):
        """Returns a string.
        """
        return self.request.session.get(
            "clinic_label_printer_name", self.user_profile.clinic_label_printer
        )

    @property
    def lab_label_printer_name(self):
        """Returns a string.
        """
        return self.request.session.get(
            "lab_label_printer_name", self.user_profile.lab_label_printer
        )

    @property
    def print_server_ip(self):
        if self.print_server_name == "localhost":
            return None
        try:
            return socket.gethostbyname(self.print_server_name)
        except (TypeError, socket.gaierror):
            return self.print_server_name

    def print_server(self):
        """Returns a CUPS connection.
        """
        cups_connection = None
        if self.print_server_name:
            try:
                if not self.print_server_ip:
                    cups_connection = cups.Connection()
                else:
                    cups_connection = cups.Connection(self.print_server_ip)
            except RuntimeError as e:
                raise PrintServerError(
                    f"Unable to connect to print server. Tried "
                    f"'{self.print_server_name}'. Got {e}"
                )
        else:
            raise PrintServerError("Print server not defined")
        return cups_connection

    @property
    def printers(self):
        """Returns a mapping of PrinterProperties objects
        or an empty mapping.
        """
        printers = {}
        cups_printers = {}
        try:
            cups_printers = self.print_server().getPrinters()
        except (RuntimeError, cups.IPPError) as e:
            raise PrinterError(
                f"Unable to list printers from print server. "
                f"Tried '{self.print_server_name}'. Got {e}"
            )
        for name in cups_printers:
            printer = Printer(
                name=name,
                print_server_func=self.print_server,
                print_server_name=self.print_server_name,
                print_server_ip=self.print_server_ip,
            )
            printers.update({name: printer})
        return printers

    @property
    def clinic_label_printer(self):
        """Returns a PrinterProperties object or None.
        """
        try:
            return self.printers.get(self.clinic_label_printer_name)
        except AttributeError:
            pass
        return None

    @property
    def lab_label_printer(self):
        """Returns a PrinterProperties object or None.
        """
        try:
            return self.printers.get(self.lab_label_printer_name)
        except AttributeError:
            pass
        return None
