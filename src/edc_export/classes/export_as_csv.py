import csv

from django.http import HttpResponse

from .base_export_model import BaseExportModel


class ExportAsCsv(BaseExportModel):

    @property
    def file_obj(self):
        """Returns a file object for the writer."""
        if not self._file_obj:
            self._file_obj = HttpResponse(mimetype='text/csv')
        self._file_obj['Content-Disposition'] = 'attachment; filename={filename}'.format(
            filename=self.export_filename)
        return self._file_obj

    def write_to_file(self):
        """Writes the export file and returns the file object."""
        exported_pk_list = []
        export_uuid_list = []
        export_file_contents = []
        writer = csv.writer(self.file_obj, delimiter=self.delimiter)
        if self.include_header_row:
            writer.writerow(self.header_row)
        for self.row_instance in self.queryset:
            row = self.fetch_row()
            writer.writerow(row)
            exported_pk_list.append(self.row_instance.pk)
            export_uuid_list.append(self.row_instance.export_uuid)
            export_file_contents.append(row)
        if self.track_history:
            self.update_export_history(exported_pk_list, export_uuid_list, export_file_contents)
        return self.file_obj
