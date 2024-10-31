# from django import forms
#
# from ..models import StockTransfer
#
#
# class StockTransferForm(forms.ModelForm):
#
#     def clean(self):
#         cleaned_data = super().clean()
#
#         # edit section one first, leave section two blank on create
#         if not self.instance.id and (
#             cleaned_data.get("bottle_count") or cleaned_data.get("barcodes")
#         ):
#             raise forms.ValidationError(
#                 "Leave bottle count and barcodes blank until AFTER preparing "
#                 "the bottles for this batch"
#             )
#
#         if (
#             cleaned_data.get("bottle_count")
#             and cleaned_data.get("bottle_count") > 0
#             and not cleaned_data.get("barcodes")
#         ):
#             raise forms.ValidationError({"bottle_count": "Expected blank or zero"})
#         if not cleaned_data.get("bottle_count") and cleaned_data.get("barcodes"):
#             raise forms.ValidationError(
#                 {"bottle_count": "Expected a number greater than zero"}
#             )
#
#         return cleaned_data
#
#     class Meta:
#         model = StockTransfer
#         fields = "__all__"
