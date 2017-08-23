import numpy as np
import pandas as pd

try:
    from django_crypto_fields.field_cryptor import FieldCryptor
except ModuleNotFoundError:
    pass


class DecryptError(Exception):
    pass


def decrypt(row, column_name, algorithm, mode):
    value = np.nan
    if pd.notnull(row[column_name]):
        field_cryptor = FieldCryptor(algorithm, mode)
        value = field_cryptor.decrypt(row[column_name])
        if value.startswith('enc1::'):
            raise DecryptError(
                f'Failed to decrypt column value {column_name}. '
                f'Perhaps check the path to the encryption keys.')
    return value
