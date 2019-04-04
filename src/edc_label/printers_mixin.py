import socket

from cups import Connection, IPPError
from django.apps import apps as django_apps
from django.utils.translation import gettext as _

from .printer import Printer


class PrinterError(Exception):
    pass


class PrintServerError(Exception):
    pass


class PrintersMixin:
    @property
    def connect_cls(self):
        return Connection

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
                    cups_connection = self.connect_cls()
                else:
                    cups_connection = self.connect_cls(self.print_server_ip)
            except RuntimeError as e:
                raise PrintServerError(
                    f"{_('Unable to connect to print server. Tried ')}"
                    f"'{self.print_server_name}'. {_('Got')} {e}"
                )
        else:
            raise PrintServerError(_("Print server not defined"))
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
        except (RuntimeError, IPPError) as e:
            raise PrinterError(
                f"{_('Unable to list printers from print server')}. "
                f"{_('Tried')} '{self.print_server_name}'. {_('Got')} {e}"
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

    def _get_label_printer(self, name):
        printer = self.printers.get(name)
        if not printer:
            raise PrinterError(
                f"{_('Printer does not exist. Got')} {name}. "
                f"{_('Installed printers are')} {list(self.printers)}."
            )
        return printer

    @property
    def clinic_label_printer(self):
        """Returns a PrinterProperties object or None.
        """
        return self._get_label_printer(self.clinic_label_printer_name)

    @property
    def lab_label_printer(self):
        """Returns a PrinterProperties object or None.
        """
        return self._get_label_printer(self.lab_label_printer_name)
