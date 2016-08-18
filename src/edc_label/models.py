import cups

from django.db import models

from django.core.exceptions import ObjectDoesNotExist

from edc_base.model.models import BaseUuidModel


class LabePrinterManager(models.Manager):

    def update_from_cups(self, cup_server_ip):
        options = {}
        conn = cups.Connection(cup_server_ip)
        printers = conn.getPrinters()
        for printer in printers:
            options.update({
                'printer_name ': printer,
                'cup_server_ip': cup_server_ip,
                'device_uri': printer['device_uri'],
                'printer_info': printer['printer-info'],
            })
            try:
                label_printer = self.get(cup_server_ip=cup_server_ip, printer_name=printer)
                label_printer.device_uri = printer['device_uri']
                label_printer.printer_info = printer['printer_info']
            except ObjectDoesNotExist:
                self.create(**options)
        return None


class LabelPrinter(BaseUuidModel):
    """A model of the printer name and IP address."""

    printer_name = models.CharField(max_length=150, unique=True)

    cups_server_ip = models.GenericIPAddressField()

    printer_info = models.CharField(max_length=250)

    device_uri = models.CharField(max_length=250)

    default = models.BooleanField(default=False)

    objects = LabePrinterManager()

    def __str__(self):
        return '{}@{}'.format(self.printer_name, self.cups_server_ip)

    class Meta:
        app_label = 'edc_label'
        ordering = ['printer_name', 'cups_server_ip']
        unique_together = ['printer_name', 'cups_server_ip']
