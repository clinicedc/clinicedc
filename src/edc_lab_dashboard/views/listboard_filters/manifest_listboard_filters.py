from edc_listboard.filters import ListboardFilter, ListboardViewFilters


class ManifestListboardViewFilters(ListboardViewFilters):
    all = ListboardFilter(name="all", label="All", lookup={})

    shipped = ListboardFilter(label="Shipped", lookup={"shipped": True})

    not_shipped = ListboardFilter(label="Not shipped", lookup={"shipped": False})

    printed = ListboardFilter(label="Printed", lookup={"printed": True})

    not_printed = ListboardFilter(label="Not printed", default=True, lookup={"printed": False})
