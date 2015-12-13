import csv

from django.http import HttpResponse

from .base_export_model import BaseExportModel


class ExportAsCsv(BaseExportModel):

    @property
    def file_obj(self):
        """Returns a file object for the writer."""
        if not self._file_obj:
            self._file_obj = HttpResponse(mimetype='text/csv')
        self._file_obj['Content-Disposition'] = 'attachment; filename={filename}'.format(filename=self.export_filename)
        return self._file_obj

    def write_to_file(self):
        """Writes the export file and returns the file object."""
        writer = csv.writer(self.file_obj, delimiter=self.delimiter)
        if self.include_header_row:
            writer.writerow(self.header_row)
        for self.row_instance in self.queryset:
            writer.writerow(self.fetch_row())
            #self.update_export_history(self.row_instance)
        return self.file_obj
