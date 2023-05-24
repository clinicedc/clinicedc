import csv
import os
from datetime import datetime

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError
from edc_constants.constants import CLOSED

from ...models import ExportPlan, ExportReceipt, ExportTransaction


class Command(BaseCommand):
    args = "<receipt filename>"
    help = "Import a receipt file for recently exported transactions."
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        header = []
        has_rejects = False
        try:
            self.ack_filename = args[0]
            _, app_label1, app_label2, self.object_name, timestamp = (
                self.ack_filename.split("/").pop().split("_")
            )
            self.app_label = app_label1 + "_" + app_label2
            self.timestamp, self.extension = timestamp.split(".")
        except IndexError:
            raise CommandError("Usage: import_receipts <receipt filename>")
        print("reading file...")
        error_filepath = os.path.join(
            os.path.expanduser(self.export_plan.target_path) or "", self.error_filename
        )
        with open(self.ack_filename, "r") as f, open(error_filepath, "w") as error_file:
            rows = csv.reader(f, delimiter="|")
            writer = csv.writer(error_file, delimiter="|")
            for row in rows:
                if not header:
                    header = row
                    writer.writerow(header)
                    continue
                try:
                    export_uuid = row[header.index("export_UUID")]
                except ValueError as e:
                    writer.writerow("error reading file. Got {0}".format(e))
                    print("Failed to process file {0}".format(self.ack_filename))
                    raise ValueError(e)
                if ExportTransaction.objects.filter(export_uuid=export_uuid):
                    for export_transaction in ExportTransaction.objects.filter(
                        export_uuid=export_uuid
                    ):
                        self.update_or_create_export_transaction(export_transaction)
                        print("  accepted: " + export_uuid)

                else:
                    has_rejects = True
                    writer.writerow(row)
                    print("  rejected: " + export_uuid)
        self.clean_up(has_rejects)

    def clean_up(self, has_rejects):
        if has_rejects:
            target_path = os.path.join(os.path.expanduser(self.export_plan.target_path))
            print("Some receipts were rejected.")
            print(f"See file {self.error_filename} in {target_path}")
        else:
            os.remove(self.error_filename)
            print("Success")

    @property
    def error_filename(self):
        try:
            app_label1, app_label2 = self.app_labe1.split("_")
            error_filename = (
                "_".join(["error", app_label1, app_label2, self.object_name, self.timestamp])
                + "."
                + self.extension
            )
        except ValueError:
            CommandError(
                "Invalid file name. Expected format xxx_app_label_objectname_timestamp.xxx. "
                "Got {0}".format(self.ack_filename)
            )
        return error_filename

    @property
    def export_plan(self):
        try:
            export_plan = ExportPlan.objects.get(
                app_label=self.app_label, object_name=self.object_name
            )
        except ExportPlan.DoesNotExist as e:
            CommandError(
                "ExportPlan not found for {0}, {1}. "
                "Check filename format or create an ExportPlan. "
                "Got {2}".format(self.app_label, self.object_name, e)
            )
        return export_plan

    def update_or_create_export_transaction(self, export_transaction):
        try:
            ExportReceipt.objects.get(export_uuid=export_transaction.export_uuid)
        except MultipleObjectsReturned:
            pass
        except ExportReceipt.DoesNotExist:
            ExportReceipt.objects.create(
                export_uuid=export_transaction.export_uuid,
                app_label=export_transaction.app_label,
                object_name=export_transaction.object_name,
                timestamp=self.timestamp,
                received_datetime=datetime.today(),
                tx_pk=export_transaction.tx_pk,
            )
        export_transaction.status = CLOSED
        export_transaction.received = True
        export_transaction.received_datetime = datetime.today()
        export_transaction.save()
