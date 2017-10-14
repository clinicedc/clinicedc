import pandas as pd

from django.conf import settings
from edc_constants.constants import YES, NO


class Helper:

    to_dataframe_cls = None

    def __init__(self, local_tz=None, date_format=None):
        self.date_format = date_format or '%Y-%m-%d %H:%M:%S.%f'
        self.local_tz = local_tz or settings.TIME_ZONE

    def get_crf_dataframe(self, model=None, cols=None):
        """Returns a CRF dataframe characterized by having an index set
        to 'subject_visit_id'.
        """
        df_crf = self.to_dataframe_cls(
            model=model, drop_sys_columns=True).dataframe
        if cols:
            cols.append('subject_visit_id')
            df_crf = df_crf[cols]
        df_crf = df_crf.set_index('subject_visit_id')
        return df_crf

    def to_local_datetime(self, s):
        """Returns a localized datetime series given tz-aware dates.
        """
        s = s.dt.tz_localize('UTC')
        s = s.dt.tz_convert(self.local_tz)
        return s

    def date_to_local_datetime(self, s):
        """Returns a localized datetime series given naive dates.
        """
        s = pd.to_datetime(s, format=self.date_format,
                           exact=True, utc=True, box=True)
        s = s.dt.tz_localize(self.local_tz)
        return s

    def get_yesno_etc(self, value):
        """Returns a value as Yes/No/not_sure given
        1, 0 True, False, etc.
        """
        try:
            value = str(int(value))
        except ValueError:
            pass
        if value in ['1', 'True']:
            value = YES
        elif value in ['0', 'False']:
            value = NO
        elif value == '2':
            value = 'not_sure'
        else:
            pass
        return value
