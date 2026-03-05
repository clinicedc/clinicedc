from django.apps import apps as django_apps
from django.contrib import messages
from django.utils.translation import gettext as _

from edc_pharmacy.constants import CENTRAL_LOCATION


def may_delete_allocation(modeladmin, request, obj=None) -> bool:
    """Hack to block delete if the stock instance has been
    transferred to a location other than CENTRAL.

    Block as if the user does not have permissions to
    delete. An additional message shows why.

    User requires explicit permission to delete this model
    (which is not the default for any role).

    See AllocationAdmin
    """
    stock_transfer_item_model_cls = django_apps.get_model("edc_pharmacy.stocktransferitem")
    if obj and (
        (
            (
                stock_transfer_item := (
                    stock_transfer_item_model_cls.objects.filter(code=obj.stock.code)
                    .order_by("stock_transfer__transfer_datetime")
                    .last()
                )
            )
            and stock_transfer_item.stock.location.name != CENTRAL_LOCATION
        )
        or obj.stock.dispensed
    ):
        if stock_transfer_item:
            msg = _(
                "%s for stock %s can't be deleted because the stock item has already "
                "been transferred to another location. See stock transfer %s."
            ) % (
                obj._meta.object_name,
                obj.stock.code,
                stock_transfer_item.stock_transfer.transfer_identifier,
            )
        else:
            msg = _(
                "%s for stock %s can't be deleted because the stock item has "
                "already been dispensed."
            ) % (obj._meta.object_name, obj.stock.code)

        modeladmin.message_user(request, msg, messages.ERROR)
        return False
    return True
