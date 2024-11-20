from __future__ import annotations

from django.apps import apps as django_apps


def get_rxrefill_model_cls():
    return django_apps.get_model("edc_pharmacy.rxrefill")


def get_rx_model_cls():
    return django_apps.get_model("edc_pharmacy.rx")


# def get_and_check_stock(stock_identifier):
#     stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
#     stock = stock_model_cls.objects.get(stock_identifier=stock_identifier)
#     if not stock.confirmed:
#         raise StockError(f"Stock item is not confirmed. Unable to process. Got {stock}.")
#     if stock.unit_qty_in - stock.unit_qty_out == Decimal(0):
#         raise InsufficientStockError(
#             f"Not in stock. Cannot repack. Got stock {stock.stock_identifier}."
#         )
#     if stock.unit_qty_in - stock.unit_qty_out < 0:
#         raise StockError(
#             "Stock `unit qty` is wrong. Unit qty IN cannot be less than unit qty OUT. "
#             f"Got stock {stock.stock_identifier}."
#         )
#     return stock


# def generate_code_with_checksum_from_id(id_number: int) -> str:
#     bytes_id = id_number.to_bytes((id_number.bit_length() + 7) // 8, "big")
#     code = base64.b32encode(bytes_id).decode("utf-8")
#     code = code.rstrip("=")
#     checksum = sum(ord(c) * (i + 1) for i, c in enumerate(code)) % 36
#     checksum_char = (
#         string.digits[checksum] if checksum < 10 else string.ascii_uppercase[checksum - 10]
#     )
#     return code + checksum_char


# def decode_code_with_checksum(code: str) -> int:
#     if code != add_checksum(code[:-1]):
#         raise ChecksumError(f"Invalid checksum for code. Got {code}")
#     padding_length = (8 - (len(code[:-1]) % 8)) % 8
#     padded_code = code[:-1] + ("=" * padding_length)
#     try:
#         decoded_bytes = base64.b32decode(padded_code)
#     except Error as e:
#         raise ValueError(f"Failed to decode string: {str(e)}")
#     return int.from_bytes(decoded_bytes, "big")


# def add_checksum(code):
#     checksum = sum(ord(c) * (i + 1) for i, c in enumerate(code)) % 36
#     checksum_char = (
#         string.digits[checksum] if checksum < 10 else string.ascii_uppercase[checksum - 10]
#     )
#     return code + checksum_char
