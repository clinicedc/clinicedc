# import re
#
# from django import forms
# from django.utils.translation import gettext as _
#
# from ..models import LabelData, StockTransferItems
#
#
# def validate_barcode_text_string(
#     value: str,
#     expected_qty: int,
#     form_field: str | None = None,
#     label: str | None = None,
#     regex: str | None = None,
# ):
#     regex = regex or r"^[A-Za-z0-9\r\n]*$"
#     if not re.match(regex, value):
#         raise forms.ValidationError(
#             {
#                 "barcodes": (
#                     f"Enter one {label} per line, no commas or spaces. "
#                     f"A {label.title()} may only contain letters and numbers."
#                 )
#             }
#         )
#     else:
#         barcode_as_list = value.split()
#         if len(barcode_as_list) != len(list(set(barcode_as_list))):
#             raise forms.ValidationError({form_field: "Must be unique list."})
#         if len(barcode_as_list) != expected_qty:
#             raise forms.ValidationError(
#                 "Counts do not match. The bottle count should match the number scanned."
#             )
#     return barcode_as_list
#
#
# class StockTransferItemsForm(forms.ModelForm):
#
#     def clean(self):
#         cleaned_data = super().clean()
#         regex = r"^[A-Za-z0-9\r\n]*$"
#         if not re.match(regex, cleaned_data["barcodes"]):
#             raise forms.ValidationError(
#                 {
#                     "barcodes": (
#                         "Enter one barcode per line, no commas or spaces. "
#                         "Barcode identifiers may only contain letters and numbers."
#                     )
#                 }
#             )
#         else:
#             if barcode_list := validate_barcode_text_string(
#                 value=cleaned_data["barcodes"],
#                 expected_qty=cleaned_data.get("bottle_count"),
#                 form_field="barcodes",
#                 label="barcode",
#                 regex=regex,
#             ):
#               qs_label_data = LabelData.objects.filter(label_batch=self.instance.label_batch)
#                 if qs_label_data.filter(reference__in=barcode_list).count() != len(
#                     barcode_list
#                 ):
#                     raise forms.ValidationError(
#                         {
#                             "barcodes": _(
#                              "Invalid barcodes found. Not all barcodes belong to this batch."
#                             )
#                         }
#                     )
#
#     class Meta:
#         model = StockTransferItems
#         fields = "__all__"
