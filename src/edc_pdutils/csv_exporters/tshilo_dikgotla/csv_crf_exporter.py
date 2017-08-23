from ..csv_crf_tables_exporter import CsvCrfTablesExporter

from .df_prepper import DfPrepper


class CsvCrfExporter(CsvCrfTablesExporter):

    df_prepper_cls = DfPrepper
