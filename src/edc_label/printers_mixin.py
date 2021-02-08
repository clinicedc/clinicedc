import socket

from cups import Connection, IPPError
from django.apps import apps as django_apps
from django.conf import settings
from django.utils.translation import gettext as _

from .constants import (
    CLINIC_LABEL_PRINTER_NAME,
    LAB_LABEL_PRINTER_NAME,
    PRINT_SERVER_NAME,
)
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
        """Returns a string."""
        return self.request.session.get(PRINT_SERVER_NAME, self.user_profile.print_server)

    @property
    def clinic_label_printer_name(self):
        """Returns a string."""
        return self.request.session.get(
            CLINIC_LABEL_PRINTER_NAME, self.user_profile.clinic_label_printer
        )

    @property
    def lab_label_printer_name(self):
        """Returns a string."""
        return self.request.session.get(
            LAB_LABEL_PRINTER_NAME, self.user_profile.lab_label_printer
        )

    @property
    def print_server_ip(self):
        if self.print_server_name == "localhost":
            return None
        try:
            return socket.gethostbyname(self.print_server_name)
        except (TypeError, socket.gaierror):
            return self.print_server_name

    @property
    def print_servers(self):
        """Returns a list of CUPS print servers.

        Default is ['localhost'].
        """
        return getattr(settings, "CUPS_SERVERS", ["localhost"])

    def print_server(self):
        """Returns a CUPS connection."""
        cups_connection = None
        if self.print_server_name:
            try:
                if not self.print_server_ip:
                    cups_connection = self.connect_cls()
                else:
                    cups_connection = self.connect_cls(self.print_server_ip)
            except (RuntimeError, IPPError) as e:
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

        If print server is not defined, raises.
        """
        printers = {}
        cups_printers = self.print_server().getPrinters()
        for name in cups_printers:
            printer = Printer(
                name=name,
                print_server_func=self.print_server,
                print_server_name=self.print_server_name,
                print_server_ip=self.print_server_ip,
            )
            printers.update({name: printer})
        return printers

    def get_label_printer(self, name):
        """Returns a PrinterProperties object, None or raises."""
        printer = self.printers.get(name)
        if not printer:
            raise PrinterError(
                f"{_('Printer does not exist. Got')} {name}. "
                f"{_('Installed printers are')} {list(self.printers)}."
            )
        return printer

    @property
    def clinic_label_printer(self):
        """Returns a PrinterProperties object or None."""
        return self.get_label_printer(self.clinic_label_printer_name)

    @property
    def lab_label_printer(self):
        """Returns a PrinterProperties object or None."""
        return self.get_label_printer(self.lab_label_printer_name)
