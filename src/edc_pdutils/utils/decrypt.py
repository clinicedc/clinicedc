import contextlib

import numpy as np
import pandas as pd
from django.core.exceptions import ImproperlyConfigured

with contextlib.suppress(ModuleNotFoundError, ImproperlyConfigured):
    from django_crypto_fields.field_cryptor import FieldCryptor


class DecryptError(Exception):
    pass


def decrypt(row, column_name, algorithm, access_mode):
    value = np.nan
    if pd.notna(row[column_name]):
        field_cryptor = FieldCryptor(algorithm, access_mode)
        value = field_cryptor.decrypt(row[column_name])
        if value.startswith("enc1::"):
            raise DecryptError(
                f"Failed to decrypt column value {column_name}. "
                f"Perhaps check the path to the encryption keys."
            )
    return value
