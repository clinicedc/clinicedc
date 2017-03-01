from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters

from edc_lab.constants import VERIFIED, SHIPPED


class PackListboardViewFilters(ListboardViewFilters):

    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    verified = ListboardFilter(
        label='Verified',
        lookup={'status': VERIFIED})

    not_verified = ListboardFilter(
        label='Not verified',
        exclude_filter=True,
        lookup={'status': VERIFIED})

    shipped = ListboardFilter(
        label='Shipped',
        lookup={'status': SHIPPED})

    not_shipped = ListboardFilter(
        label='Not shipped',
        exclude_filter=True,
        lookup={'status': SHIPPED},
        default=True)
