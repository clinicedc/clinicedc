from django_crypto_fields.field_cryptor import FieldCryptor, RSA, HASH_PREFIX
from django_crypto_fields.constants import ENCODING


def forward_hash(plaintext, algorithm=None, mode=None):
    field_cryptor = FieldCryptor(algorithm=RSA, mode='local')
    return HASH_PREFIX.encode(ENCODING) + field_cryptor.hash(plaintext)
