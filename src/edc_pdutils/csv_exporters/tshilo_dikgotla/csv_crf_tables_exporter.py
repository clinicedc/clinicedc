from ..csv_crf_tables_exporter import CsvCrfTablesExporter as Base

from .df_prepper import DfPrepper


class CsvCrfTablesExporter(Base):
    """
    ssh -f django@td.bhp.org.bw -L5001:localhost:3306 -N
    """
    df_prepper_cls = DfPrepper
    visit_column = 'maternal_visit_id'
    delimiter = ','
