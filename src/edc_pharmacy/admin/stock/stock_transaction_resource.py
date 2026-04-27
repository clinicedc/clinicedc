from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from ...models import StockTransaction
from ...models.stock.location import Location


class StockTransactionResource(resources.ModelResource):
    stock_code = fields.Field(attribute="stock__code", column_name="Stock code")
    stock_identifier = fields.Field(
        attribute="stock__stock_identifier", column_name="Stock identifier"
    )
    subject_identifier = fields.Field(column_name="Subject identifier")
    transaction_type = fields.Field(
        attribute="transaction_type", column_name="Transaction type"
    )
    transaction_datetime = fields.Field(
        attribute="transaction_datetime", column_name="Transaction datetime"
    )
    actor = fields.Field(attribute="actor__username", column_name="Actor")
    reason = fields.Field(attribute="reason", column_name="Reason")
    qty_delta = fields.Field(attribute="qty_delta", column_name="Qty delta")
    unit_qty_delta = fields.Field(
        attribute="unit_qty_delta", column_name="Unit qty delta"
    )
    from_location = fields.Field(
        attribute="from_location",
        column_name="From location",
        widget=ForeignKeyWidget(Location, field="display_name"),
    )
    to_location = fields.Field(
        attribute="to_location",
        column_name="To location",
        widget=ForeignKeyWidget(Location, field="display_name"),
    )

    class Meta:
        model = StockTransaction
        fields = (
            "stock_code",
            "stock_identifier",
            "subject_identifier",
            "transaction_type",
            "transaction_datetime",
            "actor",
            "reason",
            "qty_delta",
            "unit_qty_delta",
            "from_location",
            "to_location",
        )
        export_order = fields

    def dehydrate_subject_identifier(self, obj):
        """Pull subject from the active or ending allocation on the transaction."""
        alloc = obj.to_allocation or obj.from_allocation
        if alloc and alloc.registered_subject_id:
            return alloc.registered_subject.subject_identifier
        return obj.stock.subject_identifier or ""
