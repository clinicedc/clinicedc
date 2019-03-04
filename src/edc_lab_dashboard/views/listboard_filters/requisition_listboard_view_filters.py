from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters
from edc_lab.models import BoxItem


def get_box_items():
    return BoxItem.objects.all().values("identifier")


class RequisitionListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(name="all", label="All", lookup={})

    received = ListboardFilter(label="Received", lookup={"received": True})

    not_received = ListboardFilter(
        label="Not Received", exclude_filter=True, lookup={"received": True}
    )

    processed = ListboardFilter(label="Processed", lookup={"processed": True})

    not_processed = ListboardFilter(
        label="Not processed", exclude_filter=True, lookup={"processed": True}
    )

    packed = ListboardFilter(label="Packed", lookup={"packed": True})

    not_packed = ListboardFilter(
        label="Not packed", exclude_filter=True, lookup={"packed": True}
    )
