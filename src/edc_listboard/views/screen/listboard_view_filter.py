from ...filters import ListboardFilter
from ...filters import ListboardViewFilters as Base


class ScreeningListboardViewFilters(Base):
    all = ListboardFilter(name="all", label="All", lookup={})

    eligible = ListboardFilter(label="Eligible", position=10, lookup={"eligible": True})

    not_eligible = ListboardFilter(
        label="Not Eligible", position=11, lookup={"eligible": False}
    )

    consented = ListboardFilter(
        label="Consented", position=20, lookup={"eligible": True, "consented": True}
    )

    not_consented = ListboardFilter(
        label="Not consented",
        position=21,
        lookup={"eligible": True, "consented": False},
    )
