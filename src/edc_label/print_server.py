import cups

from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_label')


class PrintServerError(Exception):
    pass


class PrintServer:

    def __init__(self, cups_server_ip=None):
        self.error_message = None
        self.conn = None
        self.ip_address = cups_server_ip or app_config.default_cups_server_ip
        try:
            self.conn = self.connect()
        except (cups.IPPError, RuntimeError) as e:
            raise PrintServerError(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def __str__(self):
        return self.ip_address or 'localhost'

    def connect(self):
        if self.ip_address == 'localhost' or self.ip_address is None:
            return cups.Connection()
        else:
            return cups.Connection(self.ip_address)

    @property
    def printers(self):
        try:
            return self.conn.getPrinters()
        except cups.IPPError as e:
            raise PrintServerError(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def get_printer(self, name):
        try:
            return {name: self.printers[name]}
        except KeyError:
            raise PrintServerError(
                'Printer \'{}\' not found on CUPS server \'{}\'.'.format(name, self.ip_address))

    def print_file(self, *args):
        return self.conn.printFile(*args)

    @property
    def jobs(self):
        try:
            return self.conn.getJobs()
        except cups.IPPError as e:
            raise PrintServerError(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))

    def cancelJobs(self, job_ids):
        try:
            for job_id in job_ids:
                self.conn.cancelJob(job_id)
        except cups.IPPError as e:
            raise PrintServerError(
                'Unable to connect to CUPS server {}. Got \'{}\''.format(self.ip_address, str(e)))
