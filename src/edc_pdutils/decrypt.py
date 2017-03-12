import numpy as np
import pandas as pd

from django.core.exceptions import ImproperlyConfigured
from django_crypto_fields.field_cryptor import FieldCryptor


def decrypt(row, column_name, algorithm, mode):
    value = np.nan
    if pd.notnull(row[column_name]):
        field_cryptor = FieldCryptor(algorithm, mode)
        value = field_cryptor.decrypt(row[column_name])
        if value.startswith('enc1::'):
            raise ImproperlyConfigured(
                'Cannot decrypt value, specify path to the encryption keys in settings.KEYPATH')
    return value
