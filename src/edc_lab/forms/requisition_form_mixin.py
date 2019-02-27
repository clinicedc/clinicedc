class RequisitionFormMixin:

    default_item_type = "tube"
    default_item_count = 1
    default_estimated_volume = 5.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get("instance"):
            self.fields["item_type"].initial = self.default_item_type
            self.fields["item_count"].initial = self.default_item_count
            self.fields["estimated_volume"].initial = self.default_estimated_volume
        if self.fields.get("specimen_type"):
            self.fields["specimen_type"].widget.attrs["readonly"] = True
