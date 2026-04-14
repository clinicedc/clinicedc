from uuid import UUID

from django.apps import apps as django_apps


def create_new_stock_on_receive(receive_item_pk: UUID | None = None):
    receive_item_model_cls = django_apps.get_model("edc_pharmacy.receiveitem")
    stock_model_cls = django_apps.get_model("edc_pharmacy.stock")
    receive_item = receive_item_model_cls.objects.get(pk=receive_item_pk)
    create_count = (
        receive_item.item_qty_received
        - stock_model_cls.objects.filter(receive_item_id=receive_item.id).count()
    )
    if create_count > 0:
        for _ in range(0, create_count):
            stock_model_cls.objects.create(
                receive_item_id=receive_item.id,
                qty_in=1,
                qty_out=0,
                qty=1,
                container_unit_qty=receive_item.container_unit_qty,
                unit_qty_in=receive_item.container_unit_qty,
                product_id=receive_item.order_item.product.id,
                container_id=receive_item.container.id,
                location_id=receive_item.receive.location.id,
                lot_id=receive_item.lot.id,
            )
