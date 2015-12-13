import json

from datetime import datetime

from django.db.models import get_model

from edc.notification.helpers import NotificationHelper

from ..classes import ExportJsonAsCsv
from ..models import ExportPlan


class ExportHelper(object):

    def __init__(self, export_plan, exception_cls=None, notify=None, export_filename=None):
        self.reset()
        self.export_plan = export_plan
        self.export_filename = export_filename
        self.exception_cls = exception_cls or TypeError
        self.notify = False if notify is False else True  # default is to queue_notification
        self.export_failure_msg = 'Error exporting transactions for {objects} to file {filename}. Got {error}'
        self.export_success_msg = 'Successfully exported {count} transactions to file {filename} for {object}.'

    def __repr__(self):
        return '{0}({1.export_plan!r})'.format(self.__class__.__name__, self)

    def __str__(self):
        return '{0.export_plan!s}'.format(self)

    def reset(self):
        """Resets instance attr."""
        self.transactions = []
        self.export_datetime = None
        self.export_filename = None
        self.exit_status = None

    def export(self):
        """Exports decrypted model transactions to a CSV file."""
        self.exit_status = (1, 'Failed')
        self.export_datetime = datetime.today()
        try:
            self.export_filename = self.writer.write_to_file()
            self.update_history()
        except Exception as e:
            self.exit_status = (1, self.export_failure_msg.format(
                object=self, filename=self.export_filename, error=e))
        else:
            self.exit_status = (0, self.export_success_msg.format(
                count=self.export_transactions.count(), filename=self.export_filename or 'NO_FILE', object=self))
        if self.notify:
            self.queue_notification()
        return self.exit_status

    @property
    def writer(self):
        """Returns an instance of ExportJsonAsCsv for the list of transactions to export."""
        json_decoder = json.decoder.JSONDecoder()
        return ExportJsonAsCsv(
            self.transactions,
            model=self.model,
            fields=json_decoder.decode(self.export_plan.fields),
            exclude=json_decoder.decode(self.export_plan.exclude),
            extra_fields=json_decoder.decode(self.export_plan.extra_fields),
            header=self.export_plan.header,
            track_history=self.export_plan.track_history,
            show_all_fields=self.export_plan.show_all_fields,
            delimiter=self.export_plan.delimiter,
            encrypt=self.export_plan.encrypt,
            strip=self.export_plan.strip,
            target_path=self.export_plan.target_path,
            notification_plan_name=self.export_plan.notification_plan_name,
            export_datetime=self.export_datetime)

    def update_history(self):
        """Updates the export history model for this export."""
        if self.writer:
            try:
                self.writer.export_history.exit_status = self.exit_status[0]
                self.writer.export_history.exit_message = self.exit_status[1]
                self.writer.export_history.exported_datetime = self.export_datetime
                self.writer.export_history.save()
            except AttributeError:
                pass

    def queue_notification(self):
        """Writes a notification instance to be sent on the next processing of notifications (by cron)."""
        if self.export_plan.notification_plan_name:
            notification_helper = NotificationHelper()
            notification_helper.queue_notification(
                self.export_plan.notification_plan_name, self.export_filename, self.exit_status,
                export_datetime=self.export_datetime,
                transaction_count=len(self.transactions))

    @classmethod
    def update_plan(self, export_plan_setup):
        """Creates or updates the export plan model instance using a given export_plan_setup dictionary."""
        for model_config, export_plan in export_plan_setup.iteritems():
            app_label, model_name = model_config.split('.')
            model = get_model(app_label, model_name)
            try:
                export_plan_instance = ExportPlan.objects.get(
                    app_label=model._meta.app_label, object_name=model._meta.object_name)
                export_plan_instance.fields = json.dumps(export_plan.get('fields'))
                export_plan_instance.extra_fields = json.dumps(export_plan.get('extra_fields'))
                export_plan_instance.exclude = json.dumps(export_plan.get('exclude'))
                export_plan_instance.header = export_plan.get('header')
                export_plan_instance.track_history = export_plan.get('track_history')
                export_plan_instance.show_all_fields = export_plan.get('show_all_fields')
                export_plan_instance.delimiter = export_plan.get('delimiter')
                export_plan_instance.encrypt = export_plan.get('encrypt')
                export_plan_instance.strip = export_plan.get('strip')
                export_plan_instance.target_path = export_plan.get('target_path')
                export_plan_instance.notification_plan_name = export_plan.get('notification_plan_name')
                export_plan_instance.save()
            except ExportPlan.DoesNotExist:
                ExportPlan.objects.create(
                    app_label=model._meta.app_label,
                    object_name=model._meta.object_name,
                    fields=json.dumps(export_plan.get('fields')),
                    extra_fields=json.dumps(export_plan.get('extra_fields')),
                    exclude=json.dumps(export_plan.get('exclude')),
                    header=export_plan.get('header'),
                    track_history=export_plan.get('track_history'),
                    show_all_fields=export_plan.get('show_all_fields'),
                    delimiter=export_plan.get('delimiter'),
                    encrypt=export_plan.get('encrypt'),
                    strip=export_plan.get('strip'),
                    target_path=export_plan.get('target_path'),
                    notification_plan_name=export_plan.get('notification_plan_name'),
                )
