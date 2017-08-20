import tempfile

from django.apps import apps as django_apps
from django.utils import timezone

from .label_template import LabelTemplate
from .print_server import PrintServer


app_config = django_apps.get_app_config('edc_label')


class PrintLabelError(Exception):
    pass


class PrintData:
    def __init__(self, name=None, job_ids=None, copies=None, printer=None):
        self.name = name
        self.job_ids = job_ids
        if self.job_ids:
            self.print_count = len(self.job_ids)
        else:
            self.print_count = 0
        self.copies = copies
        self.printer = printer
        self.jobid = ','.join([str(i) for i in self.job_ids or [0]])


class Label:

    """A class that prepares and prints copies of labels.
    """
    label_name = 'label'
    label_template_cls = LabelTemplate
    print_server_cls = PrintServer
    printer_data_cls = PrintData
    template_name = None

    def __init__(self, template_name=None, printer_name=None):
        if template_name:
            self.template_name = template_name
        self.conn = None
        self.messages = None
        self.print_server = self.print_server_cls(
            printer_name=printer_name)
        if self.print_server.error_message:
            self.error_message = self.print_server.error_message
        self.label_template = self.label_template_cls(
            template_name=self.template_name)

    def __str__(self):
        return self.print_server.selected_printer.full_name

    def print_label(self, copies=None, context=None):
        """ Prints the label or fails silently with a message.
        """
        job_ids = []
        copies = copies or 1
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
        for i in range(copies, 0, -1):
            context.update({
                'label_count': i,
                'label_count_total': copies,
                'timestamp': timestamp})
            _, filename = tempfile.mkstemp()  # create temp file
            with open(filename, 'w') as f:
                f.write(self.label_template.render(context))
            #  note: "raw" attr is to prevent CUPS from rendering
            job_id = self.print_server.print_file(
                filename, 'edc_label', {'raw': filename})
            if not job_id:
                raise PrintLabelError('Print job failed.')
            job_ids.append(job_id)
        return self.printer_data_cls(
            name=self.label_name, copies=copies, job_ids=job_ids,
            printer=self.print_server.selected_printer.full_name)
