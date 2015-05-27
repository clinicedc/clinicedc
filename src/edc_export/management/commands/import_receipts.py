import csv
import os

from datetime import datetime

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError

from edc.constants import CLOSED

from ...models import ExportReceipt, ExportTransaction, ExportPlan


class Command(BaseCommand):

    args = '<receipt filename>'
    help = 'Import a receipt file for recently exported transactions.'
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        try:
            ack_filename = args[0]
        except IndexError:
            raise CommandError('Usage: import_receipts <receipt filename>')
        try:
            _, app_label1, app_label2, object_name, timestamp = ack_filename.split('/').pop().split('_')
            app_label = app_label1 + '_' + app_label2
            timestamp, extension = timestamp.split('.')
            header = []
            rejects = False
            error_filename = '_'.join(['error', app_label1, app_label2, object_name, timestamp]) + '.' + extension
        except ValueError as e:
            CommandError('Invalid file name. Expected format xxx_app_label_objectname_timestamp.xxx. Got {0}'.format(ack_filename))
        try:
            export_plan = ExportPlan.objects.get(app_label=app_label, object_name=object_name)
        except ExportPlan.DoesNotExist as e:
            CommandError('ExportPlan not found for {0}, {1}. Check filename format or create an ExportPlan. Got {2}'.format(app_label, object_name, e))
        target_path = export_plan.target_path
        print 'reading file...'
        with open(ack_filename, 'r') as f, open(os.path.join(os.path.expanduser(target_path) or '', error_filename), 'w') as error_file:
            rows = csv.reader(f, delimiter='|')
            writer = csv.writer(error_file, delimiter='|')
            for row in rows:
                if not header:
                    header = row
                    writer.writerow(header)
                    continue
                try:
                    export_uuid = row[header.index('export_UUID')]
                except ValueError as e:
                    writer.writerow('error reading file. Got {0}'.format(e))
                    print 'Failed to process file {0}'.format(ack_filename)
                    raise ValueError(e)
                try:
                    for export_transaction in ExportTransaction.objects.filter(export_uuid=export_uuid):
                        try:
                            ExportReceipt.objects.get(export_uuid=export_uuid)
                        except MultipleObjectsReturned:
                            pass
                        except ExportReceipt.DoesNotExist:
                            ExportReceipt.objects.create(
                                export_uuid=export_uuid,
                                app_label=app_label,
                                object_name=object_name,
                                timestamp=timestamp,
                                received_datetime=datetime.today(),
                                tx_pk=export_transaction.tx_pk,
                                )
                        export_transaction.status = CLOSED
                        export_transaction.received = True
                        export_transaction.received_datetime = datetime.today()
                        export_transaction.save()
                        print '  accepted: ' + export_uuid

                except ExportTransaction.DoesNotExist:
                    rejects = True
                    writer.writerow(row)
                    print '  rejected: ' + export_uuid
        if rejects:
            print 'Some receipts were rejected.'
            print 'See file {0} in {1}'.format(error_filename, os.path.join(os.path.expanduser(target_path)))
        else:
            try:
                os.remove(error_file.name)
            except:
                pass
            print 'Success'
