from .export_object_as_csv import ExportObjectAsCsv


class ExportDictAsCsv(ExportObjectAsCsv):

    def fetch_row(self, dct):
        """Returns one row for the writer."""
        row = []
        for field_name in self.field_names:
            value = dct[field_name]
            try:
                value = value.strftime('%Y-%m-%d %H:%M')
            except AttributeError:
                pass
            except ValueError:
                pass
            if isinstance(value, (list, tuple)):
                value = ';'.join([str(v) for v in value])
            row.append(self.strip_value(value))
        return row
