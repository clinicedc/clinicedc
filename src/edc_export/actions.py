import json
from datetime import datetime
from django.core import serializers
from django.db.models import get_model

from edc_base.encrypted_fields import FieldCryptor
from edc.export.classes import ExportAsCsv, ExportJsonAsCsv


def export_as_csv_action(description="Export selected objects to CSV",
                         fields=None, exclude=None, extra_fields=None,
                         header=True, track_history=True, show_all_fields=True,
                         delimiter=None, encrypt=True, strip=True):
    """
    Return an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row

    in my_app/admin.py add this import::
        from edc.export.actions import export_as_csv_action

    add this to your modeladmin class::
        actions = [export_as_csv_action("CSV Export",
            fields=[],
            exclude=[],
            extra_fields=[],
            )]

    use extra_fields to access field attributes from related models. Pass a
    list of dictionaries [{'label': 'query_string'}, {}, ...]

    """
    def export(modeladmin, request, queryset):
        export_as_csv = ExportAsCsv(
            queryset,
            modeladmin=modeladmin,
            fields=fields,
            exclude=exclude,
            extra_fields=extra_fields,
            header=header,
            track_history=track_history,
            show_all_fields=show_all_fields,
            delimiter=delimiter,
            export_datetime=datetime.now(),
            encrypt=encrypt,
            strip=strip)
        return export_as_csv.write_to_file()

    export.short_description = description

    return export


def export_tx_to_csv_action(description="Export transaction in each selected object to CSV",
                            fields=None, exclude=None, extra_fields=None, header=True, track_history=True,
                            show_all_fields=True, delimiter=None, encrypt=True, strip=True):

    def export(modeladmin, request, queryset):
        transactions = []
        model = None
        for qs in queryset:
            if not model:
                app_label = qs.app_label
                model_name = qs.object_name
                model = get_model(app_label, model_name)
            else:
                if not app_label == qs.app_label or not model_name == qs.object_name:
                    raise ValueError(
                        'Queryset contains transactions from more than one model. Expected ({app_label}, '
                        '{model_name}) . Got ({0}, {1}).'.format(
                            qs.app_label, qs.object_name, app_label=app_label, model_name=model_name))
            for obj in serializers.deserialize("json", FieldCryptor('aes', 'local').decrypt(qs.tx)):
                if obj.status.lower() not in ['exported', 'cancelled']:
                    obj.object.export_transaction = qs
                transactions.append(obj.object)
        export_as_csv = ExportJsonAsCsv(
            transactions,
            model=model,
            fields=fields,
            exclude=exclude,
            extra_fields=extra_fields,
            header=header,
            track_history=track_history,
            show_all_fields=show_all_fields,
            delimiter=delimiter,
            encrypt=encrypt,
            strip=strip)
        return export_as_csv.write_to_file()

    export.short_description = description

    return export


def export_file_contents(modeladmin, request, queryset):

    for qs in queryset:
        with open(qs.export_filename, 'w') as outfile:
            json.dump(qs.export_file_contents, outfile)
export_file_contents.short_description = 'Export history file contents to original file name'
