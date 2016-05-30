import hashlib
import numpy as np
import pandas as pd

from django.core.exceptions import ImproperlyConfigured
from edc.core.crypto_fields.classes import FieldCryptor


def identity(row, column_name=None):
    identity = np.nan
    column_name = column_name or 'identity'
    if pd.notnull(row[column_name]):
        field_cryptor = FieldCryptor('rsa', 'restricted')
        identity = field_cryptor.decrypt(row[column_name])
        if identity.startswith('enc1::'):
            raise ImproperlyConfigured(
                'Cannot decrypt identity, specify path to the encryption keys in settings.KEYPATH')
    return identity


def identity256(row, column_name=None):
    identity256 = np.nan
    column_name = column_name or 'identity'
    if pd.notnull(row[column_name]):
        field_cryptor = FieldCryptor('rsa', 'restricted')
        identity = field_cryptor.decrypt(row[column_name])
        if identity.startswith('enc1::'):
            raise ImproperlyConfigured(
                'Cannot decrypt identity, specify path to the encryption keys in settings.KEYPATH')
        identity256 = hashlib.sha256(identity).digest().encode("hex")
    return identity256
