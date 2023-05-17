from edc_lab.constants import PACKED, SHIPPED, VERIFIED
from edc_listboard.filters import ListboardFilter, ListboardViewFilters


class PackListboardViewFilters(ListboardViewFilters):
    all = ListboardFilter(name="all", label="All", lookup={})

    verified = ListboardFilter(label="Verified", lookup={"status": VERIFIED})

    not_verified = ListboardFilter(
        label="Not verified", exclude_filter=True, lookup={"status": VERIFIED}
    )

    packed = ListboardFilter(label="Packed", lookup={"status": PACKED})

    not_packed = ListboardFilter(
        label="Packed", exclude_filter=True, default=True, lookup={"status": PACKED}
    )

    shipped = ListboardFilter(label="Shipped", lookup={"status": SHIPPED})

    not_shipped = ListboardFilter(
        label="Not shipped", exclude_filter=True, lookup={"status": SHIPPED}
    )
